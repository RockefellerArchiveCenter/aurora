# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models

class Organization(models.Model):
    name =          models.CharField(max_length=60, unique=True)
    machine_name =	models.CharField(max_length=30, unique=True)
    created_time =  models.DateTimeField(auto_now = True)
    modified_time = models.DateTimeField(auto_now_add = True)



    def org_root_dir(self): 
    	from django.conf import settings
    	return "%s%s".format(settings.ORG_ROOT_DIR,self.machine_name)

    def save(self, *args, **kwargs):
    	from transfer_app.RAC_CMD import add_org
    	
    	results = add_org(self.name)
    	print results
    	# Run RACaddorg and on successful return code save model updated with machine_name
    		# if not successful Return message to page


        super(Organization,self).save(*args,**kwargs)

    def __unicode__(self): return self.name


class User(AbstractUser):
	organization = models.ForeignKey(Organization, null=True, blank=True)