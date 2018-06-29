# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-23 22:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0005_auto_20180521_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archives',
            name='process_status',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Transfer Started'), (20, 'Transfer Completed'), (30, 'Invalid'), (40, 'Validated'), (60, 'Rejected'), (70, 'Accepted'), (75, 'Accessioning Started'), (80, 'Archivematica Processing Started'), (85, 'Archivematica Processing Complete'), (90, 'Accession Complete')], default=20),
        ),
    ]