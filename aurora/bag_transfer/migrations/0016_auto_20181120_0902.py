# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-20 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0015_auto_20181025_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='archives',
            name='archivesspace_identifier',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='archives',
            name='archivesspace_parent_identifier',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
