# Generated by Django 2.2.10 on 2020-06-19 20:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0030_auto_20200512_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='bagit_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile_organization', to='bag_transfer.BagItProfile'),
        ),
    ]
