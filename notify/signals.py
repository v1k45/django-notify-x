from django import dispatch
from django.dispatch import receiver
from notify.models import Notification
from django.utils.translation import ugettext as _


notify = dispatch.Signal(providing_args=[
    'recipient', 'recipient_list',
    'actor', 'actor_text', 'actor_url',
    'verb', 'description', 'nf_type',
    'target', 'target_text', 'target_url',
    'obj', 'obj_text', 'obj_url',
    'extra',
])


@receiver(notify, dispatch_uid='notify_user')
def notifier(sender, **kwargs):
    recipient = kwargs.pop('recipient', None)

    recipient_list = kwargs.pop('recipient_list', None)

    verb = kwargs.pop('verb', None)
    description = kwargs.pop('description', None)
    nf_type = kwargs.pop('nf_type', 'default')

    actor = kwargs.pop('actor', None)
    actor_text = kwargs.pop('actor_text', None)
    actor_url = kwargs.pop('actor_url', None)

    target = kwargs.pop('target', None)
    target_text = kwargs.pop('target_text', None)
    target_url = kwargs.pop('target_url', None)

    obj = kwargs.pop('obj', None)
    obj_text = kwargs.pop('obj_text', None)
    obj_url = kwargs.pop('obj_url', None)

    extra = kwargs.pop('extra', None)

    if recipient and recipient_list:
        raise TypeError(_("You must specify either a single recipient or a list"
                        " of recipients, not both."))
    elif not recipient and not recipient_list:
        raise TypeError(_("You must specify the recipient of the notification."))

    if not actor and not actor_text:
        raise TypeError(_("Actor not specified."))

    if not verb:
        raise TypeError(_("Verb not specified."))

    if recipient_list and not isinstance(recipient_list, list):
        raise TypeError(_("Supplied recipient is not an instance of list."))

    if recipient:
        notification = Notification(
            recipient=recipient,
            verb=verb, description=description, nf_type=nf_type,
            actor_content_object=actor, actor_text=actor_text,
            actor_url_text=actor_url,

            target_content_object=target, target_text=target_text,
            target_url_text=target_url,

            obj_content_object=obj, obj_text=obj_text, obj_url_text=obj_url,
            extra=extra
        )
        saved_notification = notification.save()
    else:
        notifications = []
        for recipient in recipient_list:
            notifications.append(Notification(
                recipient=recipient,
                verb=verb, description=description, nf_type=nf_type,
                actor_content_object=actor, actor_text=actor_text,
                actor_url_text=actor_url,

                target_content_object=target, target_text=target_text,
                target_url_text=target_url,

                obj_content_object=obj, obj_text=obj_text,
                obj_url_text=obj_url,

                extra=extra
            ))
        saved_notification = Notification.objects.bulk_create(notifications)
    return saved_notification
