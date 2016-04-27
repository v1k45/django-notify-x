from django.template.loader import render_to_string


def render_notification(notification, render_target='', **extra):
    template_name = notification.nf_type
    template_dir = 'notifications/includes/'

    nf_ctx = {'notification': notification}
    nf_ctx.update(extra)

    suffix = '_{}'.format(render_target) if render_target and render_target != 'page' else ''
    templates = [
        "{0}{1}{2}.html".format(template_dir, template_name, suffix),
        "{0}default{1}.html".format(template_dir, suffix),
        "{0}{1}.html".format(template_dir, template_name),
        "{0}default.html".format(template_dir),
    ]

    return render_to_string(templates, nf_ctx)


def prefetch_relations(weak_queryset):
    """
    FROM: https://djangosnippets.org/snippets/2492/

    Consider such a model class::

        class Action(models.Model):
            actor_content_type = models.ForeignKey(ContentType,related_name='actor')
            actor_object_id = models.PositiveIntegerField()
            actor = GenericForeignKey('actor_content_type','actor_object_id')

    And dataset::

        Action(actor=user1).save()
        Action(actor=user2).save()

    This will hit the user table once for each action::

        [a.actor for a in Action.objects.all()]

    Whereas this will hit the user table once::

        [a.actor for a in prefetch_relations(Action.objects.all())]

    Actually, the example above will hit the database N+1 times,  where N is
    the number of actions. But with prefetch_relations(), the database will be
    hit N+1 times where N is the number of distinct content types.

    Note that prefetch_relations() is recursive.

    Here an example, making a list with prefetch_relations(), and then without
    prefetch_relations(). See the number of database hits after each test.

        In [1]: from django import db; from prefetch_relations import prefetch_relations

        In [2]: db.reset_queries()

        In [3]: x = [(a.actor, a.action_object, a.target) for a in prefetch_relations(Action.objects.all().order_by('-pk'))]

        In [4]: print len(db.connection.queries)
        34

        In [5]: db.reset_queries()

        In [6]: print len(db.connection.queries)
        0

        In [7]: x = [(a.actor, a.action_object, a.target) for a in Action.objects.all().order_by('-pk')]

        In [8]: print len(db.connection.queries)
        396
    """
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes.fields import GenericForeignKey

    # reverse model's generic foreign keys into a dict:
    # { 'field_name': generic.GenericForeignKey instance, ... }
    gfks = {}
    for name, gfk in weak_queryset.model.__dict__.items():
        if not isinstance(gfk, GenericForeignKey):
            continue
        gfks[name] = gfk

    data = {}
    for weak_model in weak_queryset:
        for gfk_name, gfk_field in gfks.items():
            related_content_type_id = getattr(
                weak_model,
                gfk_field.model._meta.get_field(gfk_field.ct_field).get_attname())
            if not related_content_type_id:
                continue
            related_content_type = ContentType.objects.get_for_id(related_content_type_id)
            related_object_id = int(getattr(weak_model, gfk_field.fk_field))

            if related_content_type not in data.keys():
                data[related_content_type] = []
            data[related_content_type].append(related_object_id)

    for content_type, object_ids in data.items():
        model_class = content_type.model_class()
        models = prefetch_relations(model_class.objects.filter(pk__in=object_ids).select_related())
        for model in models:
            for weak_model in weak_queryset:
                for gfk_name, gfk_field in gfks.items():
                    related_content_type_id = getattr(
                        weak_model,
                        gfk_field.model._meta.get_field(gfk_field.ct_field).get_attname())
                    if not related_content_type_id:
                        continue
                    related_content_type = ContentType.objects.get_for_id(related_content_type_id)
                    related_object_id = int(getattr(weak_model, gfk_field.fk_field))

                    if related_object_id != model.pk:
                        continue
                    if related_content_type != content_type:
                        continue

                    setattr(weak_model, gfk_name, model)

    return weak_queryset
