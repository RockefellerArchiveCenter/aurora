# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-17 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0005_auto_20170817_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='testfile',
            field=models.CharField(default='', max_length=120),
            preserve_default=False,
        ),
    ]
