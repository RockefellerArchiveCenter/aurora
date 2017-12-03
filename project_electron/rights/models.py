# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from orgs.models import Organization, Archives

class RightsStatement(models.Model):
    organization = models.ForeignKey(Organization)
    archive = models.ForeignKey(Archives, null=True, blank=True)
    APPLIES_TO_TYPE_CHOICES = ( # Eventually this should be replaced by a call to get record types associated with this organization
        ('administrative records', 'Administrative Records'),
        ('annual reports', 'Annual Reports'),
        ('board materials', 'Board Materials'),
        ('communications and publications', 'Communications and Publications'),
        ('grant records', 'Grant Records'),
    )
    appliestotype = models.CharField(choices=APPLIES_TO_TYPE_CHOICES, max_length=100)
    RIGHTS_BASIS_CHOICES = (
        ('Copyright', 'Copyright'),
        ('Statute', 'Statute'),
        ('License', 'License'),
        ('Other', 'Other')
    )
    rightsbasis = models.CharField(choices=RIGHTS_BASIS_CHOICES, max_length=64)

class RightsStatementCopyright(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    PREMIS_COPYRIGHT_STATUSES = (
        ('copyrighted', 'copyrighted'),
        ('public domain', 'public domain'),
        ('unknown', 'unknown'),
    )
    copyrightstatus = models.CharField(choices=PREMIS_COPYRIGHT_STATUSES, default='unknown', max_length=64)
    copyrightjurisdiction = models.CharField(max_length=2)
    copyrightexpirationperiod = models.PositiveSmallIntegerField()
    copyrightstatusdeterminationdate = models.DateField(blank=True, null=True)
    copyrightapplicablestartdate = models.DateField(blank=True, null=True)
    copyrightapplicableenddate = models.DateField(blank=True, null=True)
    copyrightenddateopen = models.BooleanField(default=False)
    copyrightnote = models.TextField()

class RightsStatementLicense(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    licenseterms = models.TextField(blank=True, null=True)
    licenseapplicablestartdate = models.DateField(blank=True, null=True)
    licenseapplicableenddate = models.DateField(blank=True, null=True)
    licenseenddateopen = models.BooleanField(default=False)
    licensenote = models.TextField()

class RightsStatementRightsGranted(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
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
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    enddateopen = models.BooleanField(default=False)
    rightsgrantednote = models.TextField()
    RESTRICTION_CHOICES = (
        ('allow', 'Allow'),
        ('disallow', 'Disallow'),
        ('conditional', 'Conditional'),
    )
    restriction = models.CharField(choices=RESTRICTION_CHOICES, max_length=64)

class RightsStatementStatuteInformation(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    statutejurisdiction = models.CharField(max_length=2)
    statutecitation = models.TextField()
    statutedeterminationdate = models.DateField(blank=True, null=True)
    statuteapplicablestartdate = models.DateField(blank=True, null=True)
    statuteapplicableenddate = models.DateField(blank=True, null=True)
    statuteenddateopen = models.BooleanField(default=False)
    statutenote = models.TextField()

class RightsStatementOtherRightsInformation(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    OTHER_RIGHTS_BASIS_CHOICES = (
        ('Donor', 'Donor'),
        ('Policy', 'Policy'),
    )
    otherrightsbasis = models.CharField(choices=OTHER_RIGHTS_BASIS_CHOICES, max_length=64)
    donorembargoperiod = models.PositiveSmallIntegerField()
    otherrightsapplicablestartdate = models.DateField(blank=True, null=True)
    otherrightsapplicableenddate = models.DateField(blank=True, null=True)
    otherrightsenddateopen = models.BooleanField(default=False)
    otherrightsnote = models.TextField()
