# Generated by Django 3.2.5 on 2021-07-28 15:33

from django.db import migrations


def set_organization(apps, schema_editor):
    """Sets the organization attribute on BagItProfile instances."""
    BagItProfile = apps.get_model('bag_transfer', 'BagItProfile')
    Organization = apps.get_model('bag_transfer', 'Organization')
    for profile in BagItProfile.objects.all():
        profile_org = Organization.objects.filter(bagit_profile=profile)[0]
        profile.organization = profile_org
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0037_auto_20210728_1133'),
    ]

    operations = [
        migrations.RunPython(set_organization)
    ]
