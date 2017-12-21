# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from orgs.models import RecordCreators

class Accession(models.Model):
    title =             models.CharField(max_length=256)
    accession_number =  models.CharField(max_length=10)
    accession_date =    models.DateTimeField(auto_now_add=True)
    start_date =        models.DateTimeField()
    end_date =          models.DateTimeField()
    extent_files =      models.PositiveIntegerField()
    extent_size =       models.PositiveIntegerField()
    creators =          models.ManyToManyField(RecordCreators)
    description =       models.TextField()
    access_restrictions =   models.TextField()
    use_restrictions =      models.TextField()
    resource =              models.URLField()
    acquisition_type =      models.CharField(max_length=200)
    appraisal_note =        models.TextField(blank=True, null=True)
