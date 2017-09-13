# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from transfer_app.RAC_CMD import *
from django.urls import reverse

class Organization(models.Model):
    is_active =     models.BooleanField(default=True)
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
    def get_absolute_url(self):
        return reverse('orgs-edit', kwargs={'pk': self.pk})


class User(AbstractUser):
    organization = models.ForeignKey(Organization, null=True, blank=False)
    machine_user = models.CharField(max_length = 10, blank=True, null=True,unique=True)
    is_machine_account = models.BooleanField(default=True)

    AbstractUser._meta.get_field('email').blank = False


    def save(self, *args, **kwargs):

        if self.pk is None:

            if self.is_machine_account:

                company_prefix = 'ra'
                # get next RA to assign
                last_machine_name = User.objects.filter(username__startswith=company_prefix).order_by('-machine_user')[:1]
                
                if last_machine_name:
                    last_machine_num = last_machine_name[0].username[len(company_prefix):]
                    last_machine_num_length = len(last_machine_num)
                    actual_num = int(last_machine_num)
                    actual_num_length = len(str(actual_num))

                    pre_zeros = ['0' for z in range(last_machine_num_length-actual_num_length)]
                    

                    new_machine_name = "{}{}{}".format(
                        company_prefix, "".join(pre_zeros) , (actual_num + 1)
                    )

                    # checks then returns system user
                    if (add_user(new_machine_name,self.organization.machine_name)):

                        self.machine_user = self.username = new_machine_name
                        print 'USER being Added: {}'.format(new_machine_name)
                    else:
                        # handle it not going as expected
                        go = 0
                    


                

        super(User,self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('users-edit', kwargs={'pk': self.pk})