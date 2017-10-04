# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from orgs.models import Archives

class BAGLogCodes(models.Model):
    code_short = models.CharField(max_length=5)
    code_types = (
        ('T', 'Transfer'),
        ('E', 'Error'),
        ('I', 'Info'),

    )
    code_type = models.CharField(max_length=5, choices=code_types)
    code_desc = models.CharField(max_length=60)
    def __unicode__(self):
        return "{} : {}".format(self.code_short,self.code_desc)

class BAGLog(models.Model):
    code = models.ForeignKey(BAGLogCodes)
    archive = models.ForeignKey(Archives, blank=True,null=True)
    log_info = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        val = "-- : {}".format(self.code.code_desc)
        if self.archive:
            val = "{} : {}".format( self.archive.bag_or_failed_name(), self.code.code_desc)
        return val

    @classmethod
    def log_it(cls, code, archive=None):
        try:
            item = cls(
                code = BAGLogCodes.objects.get(code_short=code),
                archive = archive
            ).save()
            return True
        except Exception as e:
            print e
        else:
            return False



