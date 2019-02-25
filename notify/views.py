from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseBadRequest, \
                        HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.views.decorators.http import require_POST

from .models import Notification, Response
from .notify_settings import PAGE_SIZE
from .utils import render_notification

# TODO: Convert function-based views to Class-based views.

class NotificationsList(View):

    def get_queryset(self, filter_=None, page=None):
        queryset = Notification.objects.active().prefetch().filter(recipient=self.request.user)
        paginator = Paginator(queryset, PAGE_SIZE)
        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            notifications = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            notifications = paginator.page(paginator.num_pages)
        if filter_ == 'read':
            notifications = notifications.read()
        elif filter_ == 'unread':
            notifications = notifications.unread()
        return [
            notifications,
            notifications.has_next(),
            notifications.has_previous(),
            paginator.num_pages
        ]

    def get(self, request):
        filter_ = self.request.GET.get('filter')
        page = request.GET.get('page')
        [queryset, has_next, has_prev, num_pages] = self.get_queryset(filter_, page)
        notifications = [item.as_json() for item in queryset]
        notifications = {
            'pageInfo': {
                'hasNextPage': has_next,
                'hasPrevPage': has_prev,
                'numPages': num_pages,
            },
            'data': notifications,
        }
        return JsonResponse(notifications, status=200, safe=False)


def notification_redirect(request, ctx):
    """
    Helper to handle HTTP response after an action is performed on notification

    :param request: HTTP request context of the notification

    :param ctx: context to be returned when a AJAX call is made.

    :returns: Either JSON for AJAX or redirects to the calculated next page.
    """
    if request.is_ajax():
        return JsonResponse(ctx, status=ctx.get('status', 500))
    else:
        next_page = request.POST.get('next', reverse('notifications:all'))
        if not ctx['success']:
            return HttpResponseBadRequest(ctx['msg'])
        if is_safe_url(next_page):
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect(reverse('notifications:all'))


@login_required
def notifications(request):
    """
    Returns a rendered page of all notifications for the logged-in user.
    Uses ``notification.nf_type`` as the template for individual notification.
    Each notification type is expected to have a render template
    at ``notifications/includes/NOTIFICATION_TYPE.html``.

    :param request: HTTP request context.

    :return: Rendered notification list page.
    """
    notification_list = request.user.notifications.active().prefetch()
    return render(request, 'notifications/all.html',
                  {'notifications': notification_list})


@login_required
@require_POST
def mark(request):
    """
    Handles marking of individual notifications as read or unread.
    Takes ``notification id`` and mark ``action`` as POST data.

    :param request: HTTP request context.

    :returns: Response to mark action of supplied notification ID.
    """
    notification_id = request.POST.get('id', None)
    action = request.POST.get('action', None)
    success = True

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user)
            if action == 'read':
                status = notification.mark_as_read()
                msg = _("Marked as read")
            elif action == 'unread':
                status = notification.mark_as_unread()
                msg = _("Marked as unread")
            else:
                success = False
                msg = _("Invalid mark action.")
                status = Response.HTTP_400_BAD_REQUEST
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
            status = Response.HTTP_400_BAD_REQUEST
    else:
        success = False
        msg = _("Invalid Notification ID")
        status = Response.HTTP_400_BAD_REQUEST

    ctx = {'msg': msg, 'success': success, 'action': action, 'status': status}

    return notification_redirect(request, ctx)


@login_required
@require_POST
def mark_read(request):
    """
    Handles marking of individual notifications as read.
    Takes ``notification id`` as POST data.

    :param request: HTTP request context.

    :returns: Response to mark action of supplied notification ID.
    """
    notification_id = request.POST.get('id', None)
    success = False

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user)
            status = notification.mark_as_read()
            msg = _("Marked as read")
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
            status = Response.HTTP_400_BAD_REQUEST
    else:
        success = False
        msg = _("Invalid Notification ID")
        status = Response.HTTP_400_BAD_REQUEST

    ctx = {'msg': msg, 'success': success, 'status': status}

    return notification_redirect(request, ctx)


@login_required
@require_POST
def mark_unread(request):
    """
    Handles marking of individual notifications as read.
    Takes ``notification id`` as POST data.

    :param request: HTTP request context.

    :returns: Response to mark action of supplied notification ID.
    """
    notification_id = request.POST.get('id', None)
    success = False

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user)
            status = notification.mark_as_unread()
            msg = _("Marked as unread")
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
            status = Response.HTTP_400_BAD_REQUEST
    else:
        success = False
        msg = _("Invalid Notification ID")
        status = Response.HTTP_400_BAD_REQUEST

    ctx = {'msg': msg, 'success': success, 'status': status}

    return notification_redirect(request, ctx)


@login_required
@require_POST
def mark_all(request):
    """
    Marks notifications as either read or unread depending of POST parameters.
    Takes ``action`` as POST data, it can either be ``read`` or ``unread``.

    :param request: HTTP Request context.

    :return: Response to mark_all action.
    """
    action = request.POST.get('action', None)
    success = True

    if action == 'read':
        responses = request.user.notifications.read_all()
        status = Response.HTTP_200_OK
        msg = _("Marked all notifications as read")
    elif action == 'unread':
        responses = request.user.notifications.unread_all()
        status = Response.HTTP_200_OK
        msg = _("Marked all notifications as unread")
    else:
        msg = _("Invalid mark action")
        success = False
        status = Response.HTTP_400_BAD_REQUEST
        responses = []

    ctx = {'msg': msg, 'success': success, 'action': action, 'status': status, 'responses': responses}

    return notification_redirect(request, ctx)


@login_required
@require_POST
def delete(request):
    """
    Deletes notification of supplied notification ID.

    Depending on project settings, if ``NOTIFICATIONS_SOFT_DELETE``
    is set to ``False``, the notifications will be deleted from DB.
    If not, a soft delete will be performed.

    By default, notifications are deleted softly.

    :param request: HTTP request context.

    :return: Response to delete action on supplied notification ID.
    """
    notification_id = request.POST.get('id', None)
    success = True
    read = 0

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user)
            soft_delete = getattr(settings, 'NOTIFY_SOFT_DELETE', True)
            if notification.read == False:
                read = 1
            if soft_delete:
                notification.deleted = True
                notification.save()
                status = Response.HTTP_200_OK
            else:
                notification.delete()
                status = Response.HTTP_200_OK
            msg = _("Deleted notification successfully")
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
            status = Response.HTTP_400_BAD_REQUEST
    else:
        success = False
        msg = _("Invalid Notification ID")
        status = Response.HTTP_400_BAD_REQUEST

    ctx = {'msg': msg, 'success': success, 'status': status, 'read': read}

    return notification_redirect(request, ctx)


@login_required
def notification_update(request):
    """
    Handles live updating of notifications, follows ajax-polling approach.

    Read more: http://stackoverflow.com/a/12855533/4726598

    Required URL parameters: ``flag``.

    Explanation:

        - The ``flag`` parameter carries the last notification ID \
        received by the user's browser.

        - This ``flag`` is most likely to be generated by using \
        a simple JS/JQuery DOM. Just grab the first element of \
        the notification list.

            - The element will have a ``data-id`` attribute set to the \
            corresponding notification.
            - We'll use it's value as the flag parameter.

        - The view treats the ``last notification flag`` as a model \
        ```filter()`` and fetches all notifications greater than \
        the flag for the user.

        - Then the a JSON data is prepared with all necessary \
        details such as, ``verb``, ``actor``, ``target`` and their \
        URL etc. The foreignkey are serialized as their \
        default ``__str__`` value.

            - Everything will be HTML escaped by django's ``escape()``.

        - Since these notification sent will only serve temporarily \
        on the notification box and will be generated fresh \
        using a whole template, to avoid client-side notification \
        generation using the JSON data, the JSON data will also \
        contain a rendered HTML string so that you can easily \
        do a JQuery ``$yourNotificationBox.prepend()`` on the \
        rendered html string of the notification.

        - The template used is expected to be different than the \
        template used in full page notification as the css \
        and some other elements are highly likely to be \
        different than the full page notification list. \

        - The template used will be the ``notification type`` of the \
        notification suffixed ``_box.html``. So, if your \
        notification type is ``comment_reply``, the template \
        will be ``comment_reply_box.html``.

            - This template will be stored in ``notifications/includes/`` \
            of  your template directory.

            - That makes: ``notifications/includes/comment_reply_box.html``

        - The rest is self-explanatory.

    :param request: HTTP request context.

    :return: Notification updates (if any) in JSON format.
    """
    flag = request.GET.get('flag', None)
    target = request.GET.get('target', 'box')
    last_notification = int(flag) if flag.isdigit() else None

    if last_notification:

        new_notifications = request.user.notifications.filter(
            id__gt=last_notification).active().prefetch()

        msg = _("Notifications successfully retrieved.") \
            if new_notifications else _("No new notifications.")
        notification_list = []
        for nf in new_notifications:
            notification = nf.as_json()
            notification_list.append(notification)
            notification['html'] = render_notification(
                nf, render_target=target, **notification)

        ctx = {
            "retrieved": len(new_notifications),
            "unread_count": request.user.notifications.unread().count(),
            "notifications": notification_list,
            "success": True,
            "msg": msg,
            "status": Response.HTTP_200_OK,
        }

        return JsonResponse(ctx)

    else:
        msg = _("Notification flag not sent.")
        status = Response.HTTP_400_BAD_REQUEST

    ctx = {"success": False, "msg": msg, 'status': status}
    return JsonResponse(ctx)


@login_required
def read_and_redirect(request, notification_id):
    """
    Marks the supplied notification as read and then redirects
    to the supplied URL from the ``next`` URL parameter.

    **IMPORTANT**: This is CSRF - unsafe method.
    Only use it if its okay for you to mark notifications \
    as read without a robust check.

    :param request: HTTP request context.
    :param notification_id: ID of the notification to be marked a read.

    :returns: Redirect response to a valid target url.
    """
    notification_page = reverse('notifications:all')
    next_page = request.GET.get('next', notification_page)

    if is_safe_url(next_page):
        target = next_page
    else:
        target = notification_page
    try:
        user_nf = request.user.notifications.get(pk=notification_id)
        if not user_nf.read:
            user_nf.mark_as_read()
    except Notification.DoesNotExist:
        pass

    return HttpResponseRedirect(target)
