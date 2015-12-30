from django.template.loader import render_to_string
from django.utils.timezone import datetime, make_aware, is_naive


def render_notification(notification, render_target='page', **extra):
    template_name = notification.nf_type
    template_dir = 'notifications/includes/'

    nf_ctx = {'notification': notification}
    nf_ctx.update(extra)

    suffix = '_box' if render_target == 'box' else ''
    templates = [
        "{0}{1}{2}.html".format(template_dir, template_name, suffix),
        "{0}{1}.html".format(template_dir, template_name),
        "{0}default{1}.html".format(template_dir, suffix),
    ]

    return render_to_string(templates, nf_ctx)


def to_timestamp(dt):
    epoch = datetime(1970, 1, 1)
    if is_naive(dt):
        dt = make_aware(dt)
    td = dt - make_aware(epoch)
    return td.total_seconds()
