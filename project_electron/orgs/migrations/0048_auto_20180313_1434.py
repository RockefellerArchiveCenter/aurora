# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-13 18:34
from __future__ import unicode_literals

from django.db import migrations


def update_codes(apps, schema_editor):
    # Update bag log codes to new values
    BAGLogCodes = apps.get_model('orgs', 'BAGLogCodes')
    for code in BAGLogCodes.objects.all():
        if code.code_type == 'T':
            code.code_type = 'BE'
        if code.code_type == 'E':
            code.code_type = 'GE'
        code.save()


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0047_auto_20180227_1513'),
    ]

    operations = [
        migrations.RunPython(update_codes),
    ]
