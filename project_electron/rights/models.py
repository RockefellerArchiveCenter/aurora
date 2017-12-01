# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class RightsStatement(models.Model):
    organization = models.ForeignKey(Organization)
    archive = models.ForeignKey(Archives, null=True, blank=True)
    RIGHTS_BASIS_CHOICES = (
        ('Copyright', 'Copyright'),
        ('Statute', 'Statute'),
        ('License', 'License'),
        ('Donor', 'Donor'),
        ('Policy', 'Policy'),
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
    copyrightstatus = models.TextField(choices=PREMIS_COPYRIGHT_STATUSES, default='unknown')
    copyrightjurisdiction = models.TextField()
    copyrightstatusdeterminationdate = models.TextField(blank=True, null=True)
    copyrightapplicablestartdate = models.TextField(blank=True, null=True)
    copyrightapplicableenddate = models.TextField(blank=True, null=True)
    copyrightenddateopen = models.BooleanField(default=False)
    copyrightnote = models.TextField()

class RightsStatementLicense(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    licenseterms = models.TextField(blank=True, null=True)
    licenseapplicablestartdate = models.TextField(blank=True, null=True)
    licenseapplicableenddate = models.TextField(blank=True, null=True)
    licenseenddateopen = models.BooleanField(default=False)
    licensenote = models.TextField()

class RightsStatementRightsGranted(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    act = models.TextField()
    startdate = models.TextField(blank=True, null=True)
    enddate = models.TextField(blank=True, null=True)
    enddateopen = models.BooleanField(default=False)
    rightsgrantednote = models.TextField()
    restriction = models.TextField()

class RightsStatementStatuteInformation(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    statutejurisdiction = models.TextField()
    statutecitation = models.TextField()
    statutedeterminationdate = models.TextField(blank=True, null=True)
    statuteapplicablestartdate = models.TextField(blank=True, null=True)
    statuteapplicableenddate = models.TextField(blank=True, null=True)
    statuteenddateopen = models.BooleanField(default=False)
    statutenote = models.TextField()

class RightsStatementOtherRightsInformation(models.Model):
    rightsstatement = models.ForeignKey(RightsStatement)
    otherrightsbasis = models.TextField(default='Donor')
    otherrightsapplicablestartdate = models.TextField(blank=True, null=True)
    otherrightsapplicableenddate = models.TextField(blank=True, null=True)
    otherrightsenddateopen = models.BooleanField(default=False)
    otherrightsnote = models.TextField()
