# Generated by Django 2.2.10 on 2021-07-19 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0035_auto_20210719_1528'),
    ]

    operations = [
        migrations.RenameField(
            model_name='baginfometadata',
            old_name='archive',
            new_name='transfer',
        ),
        migrations.RenameField(
            model_name='baglog',
            old_name='archive',
            new_name='transfer',
        ),
        migrations.RenameField(
            model_name='rightsstatement',
            old_name='archive',
            new_name='transfer',
        ),
    ]
