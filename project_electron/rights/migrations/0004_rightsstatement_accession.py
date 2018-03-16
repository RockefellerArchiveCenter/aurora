# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-16 19:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0048_accession'),
        ('rights', '0003_auto_20171207_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='rightsstatement',
            name='accession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orgs.Accession'),
        ),
    ]
