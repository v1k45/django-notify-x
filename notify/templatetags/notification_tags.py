from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from .. import notify_settings
from ..utils import render_notification

register = template.Library()


class RenderNotificationsNode(template.Node):

    """
    Template node to parse the token supplied and then generate html
    using the template of corresponding notification.
    """

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.split_contents()

        if tokens[1] != 'using':
            raise template.TemplateSyntaxError(
                _("The second argument in %r must be 'for'") % (tokens[0]))

        if len(tokens) == 3:
            return cls(parser.compile_filter(tokens[2]))
        elif len(tokens) == 5:
            if tokens[3] != 'for':
                raise template.TemplateSyntaxError(
                    _("The second argument in %r must be 'for'") % (tokens[0]))
            return cls(obj=parser.compile_filter(tokens[2]), target=tokens[4])
        else:
            raise template.TemplateSyntaxError(
                _("{tag} takes 2 or 3 arguments, {len} given.").format(
                    tag=tokens[0], len=len(tokens)))

    def __init__(self, obj, target=''):
        self.obj = obj
        self.target = target

    def generate_html(self, notifications):
        """
        Generates rendered HTML content using supplied notifications.
        :param notifications: Notification QuerySet Object
        :return: Rendered HTML.
        """
        html_chunks = []
        for nf in notifications:
            extra = nf.as_json() if self.target == 'box' else {}
            html = render_notification(nf, render_target=self.target, **extra)
            html_chunks.append(html)
        if not html_chunks:
            html_chunks.append(_("<b>No notifications yet.</b>"))
        html_string = '\n'.join(html_chunks)
        return html_string

    def render(self, context):
        """
        Render method of the template tag, returns generated html content to
        the parent template where it was called.
        :param context: Template context.
        :return: Generated HTML content using notification queryset object.
        """
        notifications = self.obj.resolve(context)
        return self.generate_html(notifications)


@register.tag
def render_notifications(parser, token):
    """
    Example::
        {% render_notifications using NOTIFICATION_QUERYSET_OBJECT %}
        {% render_notifications using NOTIFICATION_QUERYSET_OBJECT for \
        NOTIFICATION_RENDERING_TARGET %}

    :param parser: default arg
    :param token: default arg
    :return: Rendered HTML content for supplied notification QuerySet.
    """
    return RenderNotificationsNode.handle_token(parser, token)


JS_INCLUSION_TEMPATE = 'notifications/includes/js_variables.html'


@register.inclusion_tag(JS_INCLUSION_TEMPATE, takes_context=True)
def include_notify_js_variables(context):
    """
    Inclusion template tag to include all JS variables required by the
    notify.js file on the HTML page around <script> tags.

    Example::
        {% include_notify_js_variables %}

    :return: Prepares context for rendering in the inclusion file.
    """
    ctx = {
        'user': context['request'].user,
        'update_notification': reverse('notifications:update'),
        'mark_notification': reverse('notifications:mark'),
        'mark_read_notification': reverse('notifications:mark_read'),
        'mark_unread_notification': reverse('notifications:mark_unread'),
        'mark_all_notification': reverse('notifications:mark_all'),
        'delete_notification': reverse('notifications:delete'),

        'nf_list_class_selector': notify_settings.NF_LIST_CLASS_SELECTOR,
        'nf_read_only_list_class_selector': notify_settings.NF_READ_ONLY_LIST_CLASS_SELECTOR,
        'nf_unread_only_list_class_selector': notify_settings.NF_UNREAD_ONLY_LIST_CLASS_SELECTOR,
        'nf_class_selector': notify_settings.SINGLE_NF_CLASS_SELECTOR,
        'nf_box_list_class_selector': notify_settings.NF_BOX_CLASS_SELECTOR,
        'nf_box_class_selector': notify_settings.SINGLE_NF_BOX_CLASS_SELECTOR,

        'nf_mark_selector': notify_settings.MARK_NF_CLASS_SELECTOR,
        'nf_mark_all_selector': notify_settings.MARK_ALL_NF_CLASS_SELECTOR,
        'nf_delete_selector': notify_settings.DELETE_NF_CLASS_SELECTOR,
        'nf_mark_link_selector': notify_settings.MARK_NF_LINK_CLASS_SELECTOR,

        'nf_read_class': notify_settings.READ_NF_CLASS,
        'nf_unread_class': notify_settings.UNREAD_NF_CLASS,

        'nf_update_time_interval': notify_settings.UPDATE_TIME_INTERVAL,
    }
    return ctx


class UserNotification(RenderNotificationsNode):

    """
    Returns notifications for a supplied user, can be used as shortcut
    for render_notifications
    """
    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.split_contents()
        if len(tokens) == 1:
            # Uses the object parameter as flag
            return cls(obj='user-notification', target='page')

        if len(tokens) > 3:
            raise template.TemplateSyntaxError(_("Max arguments are two"))
        elif tokens[1] != 'for':
            raise template.TemplateSyntaxError(_("First argument must be 'for'"))
        elif not tokens[2]:
            raise template.TemplateSyntaxError(
                _("Second argument must either 'box' or 'page'"))
        else:
            return cls(obj='user-notification', target=tokens[2])

    def render(self, context):
        if self.obj == 'user-notification':
            request = context['request']
            user = request.user
            if user.is_authenticated():
                notifications = user.notifications.active().prefetch()
                return self.generate_html(notifications)
        return ''


@register.tag
def user_notifications(parser, token):
    """
    Example::
        {% user_notifications for NOTIFICATION_RENDERING_TARGET %}

    :param parser: default arg
    :param token: default arg
    :return: Rendered HTML content for supplied notification QuerySet.
    """
    return UserNotification.handle_token(parser, token)
