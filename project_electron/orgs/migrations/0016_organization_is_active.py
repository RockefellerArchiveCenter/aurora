# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-13 20:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0015_auto_20170913_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
