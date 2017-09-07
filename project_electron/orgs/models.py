# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from transfer_app.RAC_CMD import *
from django.urls import reverse

class Organization(models.Model):
    name =          models.CharField(max_length=60, unique=True)
    machine_name =  models.CharField(max_length=30, unique=True, default="orgXXX will be created here")
    created_time =  models.DateTimeField(auto_now = True)
    modified_time = models.DateTimeField(auto_now_add = True)



    def org_root_dir(self): 
        from django.conf import settings
        return "%s%s".format(settings.ORG_ROOT_DIR,self.machine_name)

    def save(self, *args, **kwargs):
        
        if self.pk is None:                         # Initial Save / Sync table
            results = add_org(self.name)
            if results[0]:
                self.machine_name = results[1]
            else:
                go = 1
                # and when it fails

        super(Organization,self).save(*args,**kwargs)

    def __unicode__(self): return self.name


class User(AbstractUser):
    organization = models.ForeignKey(Organization, null=True, blank=True,unique=True)
    machine_user = models.CharField(max_length = 10, blank=True, null=True,unique=True, default="AUTO__GEN")

    def save(self, *args, **kwargs):

        if self.pk is None:

            new_machine_name = User.objects.filter().order_by('-machine_user')[:1]
            print new_machine_name
            # results = add_user(new_machine_name)

        super(User,self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('users-edit', kwargs={'pk': self.pk})