# Generated by Django 4.0.6 on 2022-08-22 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0039_remove_organization_bagit_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='additional_error_info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='archivesspace_identifier',
            field=models.CharField(blank=True, max_length=191, null=True),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='archivesspace_parent_identifier',
            field=models.CharField(blank=True, max_length=191, null=True),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='machine_file_identifier',
            field=models.CharField(max_length=191, unique=True),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='machine_file_path',
            field=models.CharField(max_length=191),
        ),
    ]
