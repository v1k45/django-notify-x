# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gm2m.fields
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('notify', '0002_auto_20151221_0737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='actor_content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor_object_id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor_text',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor_url_text',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='obj_text',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='obj_url_text',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='target_text',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='target_url_text',
        ),
        migrations.AddField(
            model_name='notification',
            name='actors',
            field=gm2m.fields.GM2MField(through_fields=('gm2m_src', 'gm2m_tgt', 'gm2m_ct', 'gm2m_pk')),
        ),
        migrations.AddField(
            model_name='notification',
            name='modified',
            field=models.DateTimeField(default=timezone.now(), auto_now=True),
            preserve_default=False,
        ),
    ]
