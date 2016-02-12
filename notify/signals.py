from django import dispatch
from django.dispatch import receiver
from notify.models import Notification
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

notification = dispatch.Signal(
    providing_args=['recipient', 'actor', 'target', 'verb', 'nf_type',
                    'recipient_list'])


@receiver(notification)
def notifier(**kwargs):
    recipient = kwargs.pop('recipient', None)
    recipient_list = kwargs.pop('recipient_list', None)
    actor = kwargs.pop('actor', None)
    target = kwargs.pop('target', None)
    obj = kwargs.pop('obj', None)
    verb = kwargs.pop('verb', None)
    nf_type = kwargs.pop('nf_type', 'default')

    extra = kwargs.pop('extra', None)

    if recipient and recipient_list:
        raise TypeError(_("You must specify either a single recipient or "
                        "a list of recipients, not both."))
    elif not recipient and not recipient_list:
        raise TypeError(_("You must specify the recipient of notification."))

    if not actor:
        raise TypeError(_("Actor not specified."))

    if not verb:
        raise TypeError(_("Verb not specified."))

    # target, obj and actor CTs and PKs
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        target_pk = target.pk
    else:
        target_ct = None
        target_pk = None

    if obj:
        obj_ct = ContentType.objects.get_for_model(obj)
        obj_pk = obj.pk
    else:
        obj_ct = None
        obj_pk = None

    actor_ct = ContentType.objects.get_for_model(actor)
    actor_pk = actor.pk

    if recipient:
        # if notification is intended to be sent to a single user.
        nf, new = Notification.objects.get_or_create(
            recipient=recipient,
            target_content_type=target_ct,
            target_object_id=target_pk,
            obj_content_type=obj_ct,
            obj_object_id=obj_pk,
            verb=verb,
            nf_type=nf_type,
            extra=extra)

        if actor_pk not in [actor.pk for actor in nf.actors.all()]:
            nf.actors.add(actor)
            nf.read = False
            nf.save()

    else:
        # list of 'id' of recipients supplied.
        recipient_id_list = recipient_list.values_list('id', flat=True)

        # recipients who have already received this type of notification.
        current_recipient_ids = Notification.objects.filter(
            recipient_id__in=recipient_id_list,
            target_content_type=target_ct,
            target_object_id=target_pk,
            nf_type=nf_type).values_list('recipient_id', flat=True)

        # Recipient who have not received this type of notification before.
        new_recipients = list(
            set(recipient_id_list).difference(current_recipient_ids))

        # Sending notifications to new recipients.
        nfs = []
        for nf in new_recipients:
            nfs.append(
                Notification(
                    recipient_id=nf,
                    target_content_type=target_ct,
                    target_object_id=target_pk,
                    obj_content_type=obj_ct,
                    obj_object_id=obj_pk,
                    verb=verb,
                    nf_type=nf_type,
                    extra=extra,
                )
            )

        # Bulk create notifications.
        # Actors are not added at this point because ``bulk_create()``
        # currently doesn't supports M2M relations.
        Notification.objects.bulk_create(nfs)

        # All Notifications of the supplied type
        # basically old nfs + newly created nfs
        nf_list_updated = Notification.objects.filter(
            recipient_id__in=recipient_id_list,
            target_content_type=target_ct,
            target_object_id=target_pk,
            nf_type=nf_type)

        nf_id_list_updated = nf_list_updated.values_list('id', flat=True)

        # ``gm2m_src_id`` stands for notification id
        # same thing a above, extracting notifications which have
        # received notification by the supplied actors before
        duplicate_notifications = Notification.actors.through.objects.filter(
            gm2m_src_id__in=nf_id_list_updated,
            gm2m_ct_id=actor_ct.id,
            gm2m_pk=actor_pk,
        ).values_list('gm2m_src_id', flat=True)

        # notification ids which are not in the above list
        # this is done to avoid IntegrityErrors when you
        # by mistake/unknowingly add actors to a notifications which
        # already have actors which you're trying to add.
        new_notifications = list(
            set(nf_id_list_updated).difference(duplicate_notifications))

        new_actors = []
        for n in new_notifications:
            new_actors.append(
                Notification.actors.through(
                    gm2m_src_id=n,
                    gm2m_ct_id=actor_ct.id,
                    gm2m_pk=actor_pk,
                )
            )

        # Add new actors in bulk, save queries :)
        Notification.actors.through.objects.bulk_create(new_actors)

        # marking all notifications as unread
        nf_list_updated.unread_all()
