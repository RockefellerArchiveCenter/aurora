# Generated by Django 2.2.10 on 2021-07-06 19:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0033_auto_20210704_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rightsstatement',
            name='archive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rights_statements', to='bag_transfer.Archives'),
        ),
    ]
