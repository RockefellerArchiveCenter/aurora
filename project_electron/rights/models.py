# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from orgs.models import Organization, Archives

class RightsStatement(models.Model):
    organization = models.ForeignKey(Organization)
    archive = models.ForeignKey(Archives, null=True, blank=True)
    # Eventually these choices should be replaced by a call to get record types associated with this organization
    APPLIES_TO_TYPE_CHOICES = (
        ('administrative records', 'Administrative Records'),
        ('annual reports', 'Annual Reports'),
        ('board materials', 'Board Materials'),
        ('communications and publications', 'Communications and Publications'),
        ('grant records', 'Grant Records'),
    )
    applies_to_type = models.CharField(choices=APPLIES_TO_TYPE_CHOICES, max_length=100)
    RIGHTS_BASIS_CHOICES = (
        ('Copyright', 'Copyright'),
        ('Statute', 'Statute'),
        ('License', 'License'),
        ('Other', 'Other')
    )
    rights_basis = models.CharField(choices=RIGHTS_BASIS_CHOICES, max_length=64)

    def __unicode__(self):
        return '{}: {}: {}'.format(self.organization, self.applies_to_type, self.rights_basis)

    def get_rights_info_object(self):
        if self.rights_basis == 'Copyright':
            data = RightsStatementCopyright.objects.get(rights_statement=self.pk)
        elif self.rights_basis == 'License':
            data = RightsStatementLicense.objects.get(rights_statement=self.pk)
        elif self.rights_basis == 'Statute':
            data = RightsStatementStatute.objects.get(rights_statement=self.pk)
        else:
            data = RightsStatementOther.objects.get(rights_statement=self.pk)
        return data

    def get_rights_granted_objects(self):
        return RightsStatementRightsGranted.objects.filter(rights_statement=self.pk)

    def get_table_data(self):
        data = {}
        rights_info = self.get_rights_info_object()
        data['notes'] = ', '.join([value for key, value in rights_info.__dict__.items() if '_note' in key.lower()])
        return data

class RightsStatementCopyright(models.Model):
    rights_statement = models.ForeignKey(RightsStatement)
    PREMIS_COPYRIGHT_STATUSES = (
        ('copyrighted', 'copyrighted'),
        ('public domain', 'public domain'),
        ('unknown', 'unknown'),
    )
    copyright_status = models.CharField(choices=PREMIS_COPYRIGHT_STATUSES, default='unknown', max_length=64)
    copyright_jurisdiction = models.CharField(max_length=2)
    copyright_period = models.PositiveSmallIntegerField()
    copyright_status_determination_date = models.DateField(blank=True, null=True)
    copyright_applicable_start_date = models.DateField(blank=True, null=True)
    copyright_applicable_end_date = models.DateField(blank=True, null=True)
    copyright_end_date_open = models.BooleanField(default=False)
    copyright_note = models.TextField()

class RightsStatementLicense(models.Model):
    rights_statement = models.ForeignKey(RightsStatement)
    license_period = models.PositiveSmallIntegerField()
    license_terms = models.TextField(blank=True, null=True)
    license_applicable_start_date = models.DateField(blank=True, null=True)
    license_applicable_end_date = models.DateField(blank=True, null=True)
    license_end_date_open = models.BooleanField(default=False)
    license_note = models.TextField()

class RightsStatementRightsGranted(models.Model):
    rights_statement = models.ForeignKey(RightsStatement)
    rights_granted_period = models.PositiveSmallIntegerField()
    ACT_CHOICES = (
        ('publish', 'Publish'),
        ('disseminate', 'Disseminate'),
        ('replicate', 'Replicate'),
        ('migrate', 'Migrate'),
        ('modify', 'Modify'),
        ('use', 'Use'),
        ('delete', 'Delete'),
    )
    act = models.CharField(choices=ACT_CHOICES, max_length=64)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    end_date_open = models.BooleanField(default=False)
    rights_granted_note = models.TextField()
    RESTRICTION_CHOICES = (
        ('allow', 'Allow'),
        ('disallow', 'Disallow'),
        ('conditional', 'Conditional'),
    )
    restriction = models.CharField(choices=RESTRICTION_CHOICES, max_length=64)

    def __unicode__(self):
        return '{}: {}'.format(self.act, self.restriction)

class RightsStatementStatute(models.Model):
    rights_statement = models.ForeignKey(RightsStatement)
    statute_period = models.PositiveSmallIntegerField()
    statute_jurisdiction = models.CharField(max_length=2)
    statute_citation = models.TextField()
    statute_determination_date = models.DateField(blank=True, null=True)
    statute_applicable_start_date = models.DateField(blank=True, null=True)
    statute_applicable_end_date = models.DateField(blank=True, null=True)
    statute_end_date_open = models.BooleanField(default=False)
    statute_note = models.TextField()

class RightsStatementOther(models.Model):
    rights_statement = models.ForeignKey(RightsStatement)
    OTHER_RIGHTS_BASIS_CHOICES = (
        ('Donor', 'Donor'),
        ('Policy', 'Policy'),
    )
    other_rights_basis = models.CharField(choices=OTHER_RIGHTS_BASIS_CHOICES, max_length=64)
    other_rights_period = models.PositiveSmallIntegerField()
    other_rights_applicable_start_date = models.DateField(blank=True, null=True)
    other_rights_applicable_end_date = models.DateField(blank=True, null=True)
    other_rights_end_date_open = models.BooleanField(default=False)
    other_rights_note = models.TextField()
