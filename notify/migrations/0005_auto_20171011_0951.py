# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0004_auto_20170525_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='actor_text',
            field=models.CharField(max_length=200, null=True, verbose_name='Anonymous text for actor', blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='obj_text',
            field=models.CharField(max_length=200, null=True, verbose_name='Anonymous text for action object', blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='target_text',
            field=models.CharField(max_length=200, null=True, verbose_name='Anonymous text for target', blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='verb',
            field=models.CharField(max_length=200, verbose_name='Verb of the action'),
        ),
    ]
