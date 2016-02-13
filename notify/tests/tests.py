from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from notify.models import Notification
from notify.signals import notify
from django.utils import timezone
from django.core.urlresolvers import reverse
import json
from django.template import Template, Context, RequestContext
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class NotificationManagerTest(TestCase):

    def setUp(self):
        self.recipient = User.objects.create(username='recipient',
                                             email='recipient@test.com',
                                             password='pwd@recipient')
        self.actor = User.objects.create(username='actor',
                                         email='actor@test.com',
                                         password='pwd@actor')
        self.nf_count = 10

        self.assertEqual(self.recipient.id, 1)
        self.assertEqual(self.actor.id, 2)

        for x in range(self.nf_count):
            notify.send(User, recipient=self.recipient, actor=self.actor,
                        verb='followed you')

    def test_unread(self):
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)
        nf = Notification.objects.filter(recipient=self.recipient).first()
        nf.mark_as_read()
        self.assertEqual(Notification.objects.unread().count(),
                         self.nf_count - 1)

        for n in Notification.objects.unread():
            self.assertFalse(n.read)

    def test_read(self):
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)
        nf = Notification.objects.filter(recipient=self.recipient).first()
        nf.mark_as_read()
        self.assertEqual(Notification.objects.read().count(), 1)

        for n in Notification.objects.read():
            self.assertTrue(n.read)

    def test_read_all(self):
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)
        recipient_nfs = Notification.objects.filter(recipient=self.recipient)
        recipient_nfs.read_all()

        self.assertEqual(Notification.objects.read().count(), self.nf_count)
        self.assertEqual(Notification.objects.unread().count(), 0)

    def test_unread_all(self):
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)

        recipient_nfs = Notification.objects.filter(recipient=self.recipient)
        recipient_nfs.read_all()

        self.assertEqual(Notification.objects.read().count(), self.nf_count)
        self.assertEqual(Notification.objects.unread().count(), 0)

        recipient_nfs.unread_all()

        self.assertEqual(Notification.objects.read().count(), 0)
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)

    def test_delete_all_soft(self):
        self.assertEqual(Notification.objects.unread().count(), self.nf_count)

        nf = Notification.objects.filter(recipient=self.recipient).first()
        # Mark single notification as read
        nf.mark_as_read()

        self.assertEqual(Notification.objects.read().count(), 1)
        self.assertEqual(Notification.objects.unread().count(),
                         self.nf_count - 1)

        self.assertEqual(Notification.objects.active().count(), self.nf_count)
        self.assertEqual(Notification.objects.deleted().count(), 0)

        Notification.objects.delete_all()
        # Mark all as deleted
        self.assertEqual(Notification.objects.read().count(), 0)
        self.assertEqual(Notification.objects.unread().count(), 0)
        self.assertEqual(Notification.objects.active().count(), 0)
        self.assertEqual(Notification.objects.deleted().count(), self.nf_count)

        Notification.objects.active_all()
        # Mark all as active
        self.assertEqual(Notification.objects.read().count(), 1)
        self.assertEqual(Notification.objects.unread().count(),
                         self.nf_count - 1)
        self.assertEqual(Notification.objects.active().count(), self.nf_count)
        self.assertEqual(Notification.objects.deleted().count(), 0)

    @override_settings(NOTIFY_SOFT_DELETE=False)
    def test_delete_all_hard(self):
        self.assertEqual(Notification.objects.active().count(), self.nf_count)

        # Hard delete all notifications.
        Notification.objects.delete_all()
        self.assertEqual(Notification.objects.active().count(), 0)
        self.assertEqual(Notification.objects.deleted().count(), 0)


class NotificationTest(TestCase):

    def setUp(self):
        self.no_of_users = 10

        users = []
        for i in range(self.no_of_users):
            users.append(
                User(username='user-%r' % i, password='pwd@user%r' % i,
                     email='user%r@test.com' % i))
        User.objects.bulk_create(users)

        self.actor = User.objects.create(username='actor',
                                         password='pwd@actor',
                                         email='actor@test.com')

        self.recipient = User.objects.get(username='user-0')
        self.recipient_list = User.objects.filter(
            username__startswith='u').order_by('id')

    def test_created_users(self):
        users = User.objects.all()
        self.assertEqual(users.count(), self.no_of_users + 1)
        self.assertEqual(self.recipient_list.count(), self.no_of_users)

    def test_single_user_notify(self):
        notify.send(User, recipient=self.recipient, actor=self.actor,
                    verb='poked you')
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.recipient_id, self.recipient.id)
        timedelta = timezone.now() - notification.created
        self.assertLessEqual(timedelta.seconds, 60)

    def test_multiple_user_notify(self):
        notify.send(User, recipient_list=list(self.recipient_list),
                    actor=self.actor, verb='uploaded a new video')
        notifications = Notification.objects.filter(verb__startswith='u')
        self.assertEqual(notifications.count(), self.no_of_users)

        username_list = [u.username for u in self.recipient_list]

        for nf in notifications:
            self.assertIn(nf.recipient.username, username_list)
            timedelta = timezone.now() - nf.created
            self.assertLessEqual(timedelta.seconds, 60)


class NotificationViewTest(TestCase):

    def setUp(self):
        self.no_of_users = 10

        # Create recipients
        users = []
        for i in range(self.no_of_users):
            u = User(username='user-%r' % i, email='user%r@test.com' % i)
            u.set_password('pwd@user')
            users.append(u)
        User.objects.bulk_create(users)

        # Create actor
        actor = User.objects.create(username='actor',
                                    email='actor@test.com')
        actor.set_password('pwd@actor')
        actor.save()
        self.actor = User.objects.get(username="actor")

        self.recipient = User.objects.get(username='user-0')

        self.recipient_list = User.objects.filter(
            username__startswith='u').order_by('id')

        # Send notifications to all recipients.
        notify.send(User, recipient_list=list(self.recipient_list),
                    actor=self.actor, verb='wrote a new blog post.')

        # Send some more notifications to a specific user.
        self.recipient_nf_count = 11
        for i in range(10):
            notify.send(User, recipient=self.recipient, actor_text='You',
                        verb='reached level %r' % i)

        # Login this recipient
        self.assertTrue(self.client.login(username="user-0",
                                          password="pwd@user"))

    def test_created_users(self):
        users = User.objects.all()
        self.assertEqual(users.count(), self.no_of_users + 1)
        self.assertEqual(self.recipient_list.count(), self.no_of_users)
        self.assertEqual(self.recipient.id, 1)
        self.assertTrue(self.recipient.is_active)

    def test_notifications_view(self):
        response = self.client.get(reverse('notifications:all'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].count(),
                         self.recipient.notifications.count())
        self.assertEqual(response.context['notifications'].count(),
                         self.recipient_nf_count)
        self.assertTemplateUsed(response, 'notifications/all.html')

    def test_mark_notification_view_non_ajax_without_next_parameter(self):
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id
        self.assertFalse(first_nf.read)

        # Marking as read.
        response = self.client.post(reverse('notifications:mark'),
                                    {'action': 'read', 'id': first_nf_id})
        self.assertRedirects(response, reverse('notifications:all'))

        nf = Notification.objects.get(pk=first_nf_id)
        self.assertTrue(nf.read)

        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count - 1)

        # Marking as unread
        response_2 = self.client.post(reverse('notifications:mark'),
                                      {'action': 'unread', 'id': first_nf_id})
        self.assertRedirects(response_2, reverse('notifications:all'))
        nf_2 = Notification.objects.get(pk=first_nf_id)
        self.assertFalse(nf_2.read)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

    def test_mark_notification_view_non_ajax_with_next_parameter(self):
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id
        self.assertFalse(first_nf.read)

        # Marking as read
        ctx = {'action': 'read', 'id': first_nf_id, 'next': '/notifications/'}
        response = self.client.post(reverse('notifications:mark'), ctx)
        self.assertRedirects(response, 'http://testserver/notifications/',
                             target_status_code=404, status_code=302)

        nf = Notification.objects.get(pk=first_nf_id)
        self.assertTrue(nf.read)

        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count - 1)

        # Marking as unread
        ctx2 = {'action': 'unread', 'id': first_nf_id,
                'next': '/notifications/'}
        response_2 = self.client.post(reverse('notifications:mark'), ctx2)
        self.assertRedirects(response_2, 'http://testserver/notifications/',
                             target_status_code=404, status_code=302)
        nf_2 = Notification.objects.get(pk=first_nf_id)
        self.assertFalse(nf_2.read)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

    def test_mark_notification_view_ajax(self):
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id
        self.assertFalse(first_nf.read)

        # Marking as read
        ctx = {'action': 'read', 'id': first_nf_id}
        response = self.client.post(reverse('notifications:mark'), ctx,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        nf = Notification.objects.get(pk=first_nf_id)
        self.assertTrue(nf.read)

        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count - 1)

        # Marking as unread
        ctx = {'action': 'unread', 'id': first_nf_id}
        response_2 = self.client.post(reverse('notifications:mark'), ctx,
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_2.status_code, 200)
        nf_2 = Notification.objects.get(pk=first_nf_id)
        self.assertFalse(nf_2.read)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

    def test_mark_notification_view_for_arbitrary_user(self):
        """
        Our purpose here is to check whether user A can mark user B's
        notification as read or unread.
        """
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)
        self.assertNotEqual(self.recipient.id, 2)

        nf_of_other_user = Notification.objects.get(recipient_id=2)
        self.assertFalse(nf_of_other_user.read)

        ctx = {'action': 'read', 'id': nf_of_other_user.id}

        response = self.client.post(reverse('notifications:mark'), ctx)

        self.assertEqual(response.status_code, 400)

        nf_of_other_user = Notification.objects.get(recipient_id=2)
        self.assertFalse(nf_of_other_user.read)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

    # I'll escape the with and without `next` parameter test as it is
    # handled by the same functions, it is redundant to write them.

    def test_mark_all_notification_view_non_ajax(self):
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

        # Mark all as read
        ctx = {'action': 'read'}
        response = self.client.post(reverse('notifications:mark_all'), ctx)
        self.assertRedirects(response, reverse('notifications:all'))

        self.assertEqual(self.recipient.notifications.unread().count(), 0)
        self.assertEqual(self.recipient.notifications.read().count(),
                         self.recipient.notifications.count())

        # Mark all as unread
        ctx2 = {'action': 'unread'}
        response2 = self.client.post(reverse('notifications:mark_all'), ctx2)
        self.assertRedirects(response2, reverse('notifications:all'))

        self.assertEqual(self.recipient.notifications.read().count(), 0)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient.notifications.count())

    def test_mark_all_notification_view_ajax(self):
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient_nf_count)

        # Mark all as read
        ctx = {'action': 'read'}
        response = self.client.post(reverse('notifications:mark_all'), ctx,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.recipient.notifications.unread().count(), 0)
        self.assertEqual(self.recipient.notifications.read().count(),
                         self.recipient.notifications.count())

        # Mark all as unread
        ctx2 = {'action': 'unread'}
        response2 = self.client.post(reverse('notifications:mark_all'), ctx2,
                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(self.recipient.notifications.read().count(), 0)
        self.assertEqual(self.recipient.notifications.unread().count(),
                         self.recipient.notifications.count())

    def test_soft_delete_notification_view_non_ajax(self):
        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id
        self.assertFalse(first_nf.deleted)

        # Soft delete notification
        ctx = {'id': first_nf_id}
        response = self.client.post(reverse('notifications:delete'), ctx)
        self.assertRedirects(response, reverse('notifications:all'))

        nf = Notification.objects.get(pk=first_nf_id)
        self.assertTrue(nf.deleted)

        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count - 1)

    def test_soft_delete_notification_view_ajax(self):
        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id
        self.assertFalse(first_nf.deleted)

        # Soft delete notification
        ctx = {'id': first_nf_id}
        response = self.client.post(reverse('notifications:delete'), ctx,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        nf = Notification.objects.get(pk=first_nf_id)
        self.assertTrue(nf.deleted)

        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count - 1)

    @override_settings(NOTIFY_SOFT_DELETE=False)
    def test_hard_delete_notification_view(self):
        self.assertEqual(self.recipient.notifications.all().count(),
                         self.recipient_nf_count)

        first_nf = self.recipient.notifications.first()
        first_nf_id = first_nf.id

        # Hard delete notification
        ctx = {'id': first_nf_id}
        response = self.client.post(reverse('notifications:delete'), ctx)
        self.assertRedirects(response, reverse('notifications:all'))

        self.assertRaises(Notification.DoesNotExist,
                          Notification.objects.get,
                          pk=first_nf_id)

        self.assertEqual(self.recipient.notifications.all().count(),
                         self.recipient_nf_count - 1)

    def test_delete_notification_view_for_arbitrary_user(self):
        """
        Our purpose here is to check whether user A can mark user B's
        notification as read or unread.
        """
        self.assertNotEqual(self.recipient.id, 2)

        nf_of_other_user = Notification.objects.get(recipient_id=2)
        self.assertFalse(nf_of_other_user.deleted)

        ctx = {'id': nf_of_other_user.id}

        response = self.client.post(reverse('notifications:mark'), ctx)

        self.assertEqual(response.status_code, 400)

        nf_of_other_user = Notification.objects.get(recipient_id=2)
        self.assertFalse(nf_of_other_user.deleted)

        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count)

    def test_update_notifications_view(self):
        self.assertEqual(self.recipient.notifications.active().count(),
                         self.recipient_nf_count)
        nf = Notification.objects.get(pk=12)
        self.assertEqual(nf.recipient.username, 'user-0')

        url = "{}?flag=12".format(reverse('notifications:update'))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        resp = json.loads(response.content.decode('utf-8'))

        self.assertTrue(resp['success'])
        self.assertEqual(resp['unread_count'],
                         self.recipient.notifications.unread().count())
        notifications = self.recipient.notifications.active().filter(
            id__gt=12)
        self.assertEqual(resp['retrieved'],
                         notifications.count())

        for json_nf in resp['notifications']:
            self.assertIn(json_nf['id'],
                          [nf.id for nf in notifications])

    def test_update_view_with_wrong_flag_value(self):
        nf = Notification.objects.get(pk=3)
        self.assertNotEqual(nf.recipient.username, 'user-0')

        url = "{}?flag=this-wont-work".format(reverse('notifications:update'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content.decode('utf-8'))

        self.assertFalse(resp['success'])

        # A notification that does not exists
        # according to behavior described in #18, request should be successfu;
        # even if the notification ID doesn't exists/ belongs to the user.
        url2 = "{}?flag=123456789".format(reverse('notifications:update'))
        response2 = self.client.get(url2)

        self.assertEqual(response2.status_code, 200)
        resp2 = json.loads(response2.content.decode('utf-8'))

        # request is still successful
        self.assertTrue(resp2['success'])

    def test_read_and_redirect(self):
        """
        when users visits the view, they are redirected
        to the supplied next url. At the same time, the
        supplied notification id is marked as read.
        """
        nf = Notification.objects.get(pk=1)
        self.assertFalse(nf.read)
        self.assertEqual(nf.recipient.username, 'user-0')

        target_page = reverse('notifications:read_and_redirect', args=[nf.id])
        url = "{}?next=/home/".format(target_page)
        response = self.client.get(url)

        self.assertRedirects(response, "http://testserver/home/",
                             target_status_code=404, status_code=302)
        nf_new = Notification.objects.get(pk=1)
        self.assertTrue(nf_new.read)

    def test_read_and_redirect_unsafe_url(self):
        """
        when the ``next`` parameter is an unsafe url,
        user is redirected to the notifications page.
        """
        nf = Notification.objects.get(pk=1)
        self.assertFalse(nf.read)
        self.assertEqual(nf.recipient.username, 'user-0')

        target_page = reverse('notifications:read_and_redirect', args=[nf.id])
        url = "{}?next=file:///home/".format(target_page)
        response = self.client.get(url)

        self.assertRedirects(response, reverse('notifications:all'),
                             target_status_code=200, status_code=302)
        nf_new = Notification.objects.get(pk=1)
        self.assertTrue(nf_new.read)

    def test_read_and_redirect_arbitrary_notification_id(self):
        """
        When the users (attackers) change the notification id supplied
        in the URL manually to the notification id of another user (victim),
        the notification won't be marked as read.

        But the user (attacker) will still be redirected to the supplied
        next page if it is safe.
        """
        nf = Notification.objects.get(pk=3)
        self.assertFalse(nf.read)
        self.assertNotEqual(nf.recipient.username, 'user-0')

        target_page = reverse('notifications:read_and_redirect', args=[nf.id])
        url = "{}?next=/home/".format(target_page)
        response = self.client.get(url)

        self.assertRedirects(response, "http://testserver/home/",
                             target_status_code=404, status_code=302)

        nf_new = Notification.objects.get(pk=3)
        self.assertFalse(nf_new.read)


class NotificationTemplateTagTest(TestCase):

    RENDER_TEMPLATE = Template("""
    {% load notification_tags %}
    {% render_notifications using notifications for page %}
    """)

    RENDER_TEMPLATE_FOR_BOX = Template("""
    {% load notification_tags %}
    {% render_notifications using notifications for box %}
    """)

    JS_INCLUSION = Template("""
    {% load notification_tags  %}
    {% include_notify_js_variables %}
    """)

    USER_NOTIFICATIONS = Template("""
    {% load notification_tags %}
    {% user_notifications %}
    """)

    def setUp(self):
        user = User(username='user', email='user@test.com')
        user.set_password('pwd@user')
        user.save()

        self.user = User.objects.get(username='user')

        actor = User.objects.create_user('actor', 'actor@test.com',
                                         'pwd@actor')

        for x in range(10):
            notify.send(User, recipient=self.user, actor=actor,
                        verb='followed you', nf_type='followed_you')

        factory = RequestFactory()
        self.request = factory.get('/foobar/')

    def test_render_template_tag(self):
        notify.send(User, recipient=self.user,
                    actor_text='Joe', verb='followed you')
        nf_list = Notification.objects.filter(recipient=self.user).active()
        rendered = self.RENDER_TEMPLATE.render(
            Context({'notifications': nf_list}))
        self.assertIn('followed you', rendered)

    def test_render_template_tag_for_box(self):
        notify.send(User, recipient=self.user,
                    actor_text='Joe', verb='followed you')
        nf_list = Notification.objects.filter(recipient=self.user).active()
        rendered = self.RENDER_TEMPLATE_FOR_BOX.render(
            Context({'notifications': nf_list}))
        # to make things differentiable we'll use n-rTt-bx as a flag
        # in the default ``box`` template.
        self.assertIn('n-rTt-bx', rendered)
        self.assertIn('followed you', rendered)

    def test_render_template_tag_with_empty_notifications(self):
        nf_list = Notification.objects.filter(recipient=self.user).none()
        rendered = self.RENDER_TEMPLATE.render(
            Context({'notifications': nf_list}))
        self.assertIn('No notifications yet', rendered)

    def test_render_template_tag_without_context(self):
        rendered = self.RENDER_TEMPLATE.render(Context({}))
        self.assertIn('No notifications yet', rendered)

    def test_js_inclusion_tag(self):
        self.request.user = self.user
        rendered = self.JS_INCLUSION.render(RequestContext(self.request))
        self.assertIn('<script type="text/javascript">', rendered)

    def test_js_inclusion_tag_anonymous_user(self):
        self.request.user = AnonymousUser()
        rendered = self.JS_INCLUSION.render(RequestContext(self.request))
        self.assertNotIn('<script type="text/javascript">', rendered)

    def test_user_notifications(self):
        self.request.user = self.user
        rendered = self.USER_NOTIFICATIONS.render(RequestContext(self.request))
        self.assertIn('followed you', rendered)

    def test_user_notifications_for_anonymous_user(self):
        self.request.user = AnonymousUser()
        rendered = self.USER_NOTIFICATIONS.render(RequestContext(self.request))
        self.assertNotIn('followed you', rendered)

# TODO: Write test for test-worthy methods.
