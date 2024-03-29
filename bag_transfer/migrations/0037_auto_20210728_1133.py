# Generated by Django 3.2.5 on 2021-07-28 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0036_auto_20210719_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='bagitprofile',
            name='organization',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='bag_transfer.organization'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bagitprofile',
            name='source_organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.organization'),
        ),
    ]
