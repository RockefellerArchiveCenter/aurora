# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-12 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0011_auto_20170830_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='machine_user',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
