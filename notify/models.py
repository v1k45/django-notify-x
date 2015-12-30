from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.db.models import QuerySet
from jsonfield.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import escape
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from gm2m.fields import GM2MField
from .utils import to_timestamp


class NotificationQueryset(QuerySet):

    """
    Chain-able QuerySets using ```.as_manager()``.
    """

    def active(self):
        """
        QuerySet filter() for retrieving both read and unread notifications
        which are not soft-deleted.

        :return: Non soft-deleted notifications.
        """
        return self.filter(deleted=False)

    def read(self):
        """
        QuerySet filter() for retrieving read notifications.

        :return: Read and active Notifications filter().
        """
        return self.filter(deleted=False, read=True)

    def unread(self):
        """
        QuerySet filter() for retrieving unread notifications.

        :return: Unread and active Notifications filter().
        """
        return self.filter(deleted=False, read=False)

    def unread_all(self, user=None):
        """
        Marks all notifications as unread for a user (if supplied)

        :param user: Notification recipient.

        :return: Updates QuerySet as unread.
        """
        qs = self.read()
        if user:
            qs.filter(recipient=user)
        qs.update(read=False)

    def read_all(self, user=None):
        """
        Marks all notifications as read for a user (if supplied)

        :param user: Notification recipient.

        :return: Updates QuerySet as read.
        """
        qs = self.unread()
        if user:
            qs.filter(recipient=user)
        qs.update(read=True)

    def delete_all(self, user=None):
        """
        Method to soft-delete all notifications of a User (if supplied)

        :param user: Notification recipient.

        :return: Updates QuerySet as soft-deleted.
        """
        qs = self.active()
        if user:
            qs.filter(recipient=user)

        soft_delete = getattr(settings, 'NOTIFY_SOFT_DELETE', True)

        if soft_delete:
            qs.update(deleted=True)
        else:
            qs.delete()

    def active_all(self, user=None):
        """
        Method to soft-delete all notifications of a User (if supplied)

        :param user: Notification recipient.

        :return: Updates QuerySet as soft-deleted.
        """
        qs = self.deleted()
        if user:
            qs.filter(recipient=user)
        qs.update(deleted=False)

    def deleted(self):
        """
        QuerySet ``filter()`` for retrieving soft-deleted notifications.

        :return: Soft deleted notification filter()
        """
        return self.filter(deleted=True)


@python_2_unicode_compatible
class Notification(models.Model):

    """
    **Notification Model for storing notifications. (Yeah, too obvious)**

    This model is pretty-much a replica of ``django-notifications``'s
    model. The newly added fields just adds a feature to allow anonymous
    ``actors``, ``targets`` and ``object``.

    **Attributes**:
        :recipient:     The user who receives notification.
        :verb:          Action performed by actor (not necessarily).
        :description:   Option description for your notification.

        :nf_type:   | Each notification is different, they must be formatted
                    | differently during HTML rendering. For this, each
                    | notification gets to carry it own *notification type*.
                    |
                    | This notification type will be used to search
                    | the special template for the notification located at
                    | ``notifications/includes/NF_TYPE.html`` of your
                    | template directory.
                    |
                    | The main reason to add this field is to save you
                    | from the pain of writing ``if...elif...else`` blocks
                    | in your template file just for handling how
                    | notifications will get rendered.
                    |
                    | With this, you can just save template for an individual
                    | notification type and call the *template-tag* to render
                    | all notifications for you without writing a single
                    | ``if...elif...else block``.
                    |
                    | You'll just need to do a
                    | ``{% render_notifications using NOTIFICATION_OBJ %}``
                    | and you'll get your notifications rendered.
                    |
                    | By default, every ``nf_type`` is set to ``default``.

    :extra:     **JSONField**, holds other optional data you want the
                notification to carry in JSON format.

    :deleted:   Useful when you want to *soft delete* your notifications.

    """

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='notifications',
                                  on_delete=models.CASCADE,
                                  verbose_name=_('Notification receiver'))

    # actor attributes.

    actors = GM2MField()

    # basic details.
    verb = models.CharField(max_length=50,
                            verbose_name=_('Verb of the action'))

    description = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name=_('Description of the notification'))

    nf_type = models.CharField(max_length=20, default='default',
                               verbose_name=_('Type of notification'))

    # TODO: Add a field to store notification cover images.

    # target attributes.
    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        related_name='notify_target', on_delete=models.CASCADE,
        verbose_name=_('Content type of target object'))

    target_object_id = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('ID of the target object'))

    target_content_object = GenericForeignKey('target_content_type',
                                              'target_object_id')

    # obj attributes.
    obj_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        related_name='notify_object', on_delete=models.CASCADE,
        verbose_name=_('Content type of action object'))

    obj_object_id = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('ID of the target object'))

    obj_content_object = GenericForeignKey('obj_content_type', 'obj_object_id')

    extra = JSONField(null=True, blank=True,
                      verbose_name=_('JSONField to store addtional data'))

    # Advanced details.
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    read = models.BooleanField(default=False,
                               verbose_name=_('Read status'))
    deleted = models.BooleanField(default=False,
                                  verbose_name=_('Soft delete status'))

    objects = NotificationQueryset.as_manager()

    class Meta(object):
        ordering = ('-created', )

    def mark_as_read(self):
        """
        Marks notification as read
        """
        self.read = True
        self.save()

    def mark_as_unread(self):
        """
        Marks notification as unread.
        """
        self.read = False
        self.save()

    @property
    def actor(self):
        actor_count = self.actors.all().count()
        if actor_count <= 2:
            actor_list = [str(actor) for actor in self.actors.all()]
            actor_val = ' and '.join(actor_list)
        else:
            actor_first = self.actors.all().first()
            actor_val = "{0} and {1} others".format(actor_first,
                                                    actor_count - 1)
        return actor_val

    @property
    def actor_url(self):
        """
        Property to return permalink of the actor.
        Uses ``get_absolute_url()``.

        If ``get_absolute_url()`` method fails, it tries to grab URL
        from ``actor_url_text``, if it fails again, returns a "#".

        :return: URL for the actor.
        """
        try:
            url = self.actor_content_object.get_absolute_url()
        except AttributeError:
            url = "#"
        return url

    @property
    def target(self):
        """
        See ``actor`` property

        :return: Target object or Text or None
        """
        return self.target_content_object

    @property
    def target_url(self):
        """
        See ``actor_url`` property.

        :return: URL for the target.
        """
        try:
            url = self.target_content_object.get_absolute_url()
        except AttributeError:
            url = "#"
        return url

    @property
    def obj(self):
        """
        See ``actor`` property.

        :return: Action Object or Text or None.
        """
        return self.obj_content_object

    @property
    def obj_url(self):
        """
        See ``actor_url`` property.

        :return: URL for Action Object.
        """
        try:
            url = self.obj_content_object.get_absolute_url()
        except AttributeError:
            url = "#"
        return url

    @property
    def flag(self):
        return to_timestamp(self.modified)

    @staticmethod
    def do_escape(obj):
        """
        Method to HTML escape an object or set it to None conditionally.
        performs ``str()`` on the argument so that a foreignkey gets
        serialized? and spit out the ``__str__`` output instead of an Object.

        :param obj: Object to escape.

        :return: HTML escaped and JSON-friendly data.
        """
        return escape(str(obj)) if obj else None

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'description': self.description,
            'target': self.target,
            'obj': self.obj,
            'at': timesince(self.created),
        }

        if ctx['actor']:
            if not ctx['target']:
                return _("{actor} {verb} {at} ago").format(**ctx)
            elif not ctx['obj']:
                return _("{actor} {verb} on {target} {at} ago").format(**ctx)
            elif ctx['obj']:
                return _("{actor} {verb} {obj} on {target} {at} ago").format(**ctx)
        return _("{description} -- {at} ago").format(**ctx)

    def as_json(self):
        """
        Notification data in a Python dictionary to which later gets
        supplied to JSONResponse so that it gets JSON serialized
        the *django-way*

        :return: Dictionary format of the QuerySet object.
        """
        data = {
            "id": self.id,
            "actor": self.do_escape(self.actor),
            "verb": self.do_escape(self.verb),
            "read": self.read,
            "nf_type": self.do_escape(self.nf_type),
            "target": self.do_escape(self.target),
            "target_url": self.do_escape(self.target_url),
            "obj": self.do_escape(self.obj),
            "obj_url": self.do_escape(self.obj_url),
            "created": self.created,
            "updated": self.modified,
            "flag": self.flag,
        }
        return data
