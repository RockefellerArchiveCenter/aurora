# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Organization(models.Model):
    name =          models.CharField(max_length=60)
    created_time =  models.DateTimeField(auto_now = True)
    modified_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        print 'this is where we will call RAC add org'
        super(Organization,self).save(*args,**kwargs)

    def __unicode__(self): return self.name