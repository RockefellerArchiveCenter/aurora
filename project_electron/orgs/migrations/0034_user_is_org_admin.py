# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 05:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0033_auto_20171004_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_org_admin',
            field=models.BooleanField(default=False),
        ),
    ]
