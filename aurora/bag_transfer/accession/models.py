# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from bag_transfer.models import Organization, RecordCreators, LanguageCode


class Accession(models.Model):
    title = models.CharField(max_length=256)
    accession_number = models.CharField(max_length=10, null=True, blank=True)
    accession_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    extent_files = models.PositiveIntegerField()
    extent_size = models.PositiveIntegerField()
    creators = models.ManyToManyField(RecordCreators, blank=True)
    description = models.TextField()
    access_restrictions = models.TextField()
    use_restrictions = models.TextField()
    resource = models.URLField()
    acquisition_type = models.CharField(max_length=200)
    appraisal_note = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='accession', null=True, blank=True)
    language = models.ForeignKey(LanguageCode, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    CREATED = 10
    DELIVERED = 20
    PROCESS_STATUS_CHOICES = (
        (CREATED, 'Accession created'),
        (DELIVERED, 'Accession delivered to queue'),
    )
    process_status = models.PositiveSmallIntegerField(choices=PROCESS_STATUS_CHOICES, default=10, null=True, blank=True)
