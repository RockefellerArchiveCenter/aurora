# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-22 15:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0036_archives_process_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archives',
            name='process_status',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Transfer Started'), (20, 'Transfer Completed'), (30, 'Invalid'), (40, 'Validated'), (60, 'Rejected'), (70, 'Accepted'), (90, 'Accessioned')], default=20),
        ),
    ]
