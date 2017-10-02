# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from transfer_app import RAC_CMD
from django.urls import reverse

from django.contrib import messages



from transfer_app.lib.ldap_auth import LDAP_Manager

class Organization(models.Model):
    is_active =     models.BooleanField(default=True)
    name =          models.CharField(max_length=60, unique=True)
    machine_name =  models.CharField(max_length=30, unique=True, default="orgXXX will be created here")
    created_time =  models.DateTimeField(auto_now = True)
    modified_time = models.DateTimeField(auto_now_add = True)

    def org_users(self):
        return User.objects.filter(organization=self).order_by('username')

    def org_root_dir(self): 
        from django.conf import settings
        return "%s%s".format(settings.ORG_ROOT_DIR,self.machine_name)

    def save(self, *args, **kwargs):
        
        if self.pk is None:                         # Initial Save / Sync table
            results = RAC_CMD.add_org(self.name)
            if results[0]:
                self.machine_name = results[1]
            else:
                go = 1
                # and when it fails
        super(Organization,self).save(*args,**kwargs)

    @staticmethod
    def users_by_org():
        orgs = Organization.objects.all().order_by('name')
        if not orgs: return False
        data = []

        for org in orgs:
            data.append({
                'org' : org,
                'users': org.org_users()
            })
        return data

    @staticmethod
    def is_org_active(org):
        
        ## DOES ORG EXIST
        organization = {}
        try:
            organization = Organization.objects.get(machine_name=org)
        except Organization.DoesNotExist as e:
            print e
        if not organization:
            print 'org doesnt exist log and continue to next file'
            return False

        ## ORG ACTIVE
        if not organization.is_active:
            print 'org not acitve, log and continue'
            return False
        return organization

    def __unicode__(self): return self.name
    def get_absolute_url(self):
        return reverse('orgs-edit', kwargs={'pk': self.pk})

class User(AbstractUser):

    organization = models.ForeignKey(Organization, null=True, blank=False)
    is_machine_account = models.BooleanField(default=True)

    from_ldap = models.BooleanField(editable=False, default=False)
    is_new_account = models.BooleanField(default=False)

    AbstractUser._meta.get_field('email').blank = False

    def save(self, *args, **kwargs):

        if self.from_ldap:
            orig = User.objects.get(pk=self.pk)
            if orig.organization != self.organization:

                ## SHOULD ACTUALLY REMOVE ANY GROUPS THAT MATCH REGEX ORGXXX
                if orig.organization:
                    # remove from ORG
                    if RAC_CMD.del_from_org(self.username,orig.organization.machine_name):
                        print 'here'
                        if RAC_CMD.add2grp(self.organization.machine_name,self.username):
                            print 'GROUP CHANGED'
                else:
                    if RAC_CMD.add2grp(self.organization.machine_name,self.username):
                        print 'GROUP CHANGED'


        super(User,self).save(*args,**kwargs)

    @staticmethod
    def refresh_ldap_accounts():
        ldap_man = LDAP_Manager()

        new_accounts = 0

        if ldap_man.get_all_users():

            ldapusers = [u.lower() for u in User.objects.filter(from_ldap=True).values_list('username',flat=True)]


            for uid in ldap_man.users:
                uid = uid.strip().lower()
                if uid not in ldapusers:
                    # CREATE USER ACCOUNT ON SERVER
                    if RAC_CMD.add_user(uid):
                        new_user = User.objects.create_user(uid,None,None)
                        new_user.is_active = False
                        new_user.from_ldap = True
                        new_user.is_new_account = True
                        new_user.save()
                        new_accounts += 1
        return new_accounts


    @staticmethod
    def is_user_active(u,org):
        user = {}
        try:
            print 'i am here'
            user = User.objects.get(username = u, organization =org)
        except User.DoesNotExist as e:
            print e
        if not user:
            print 'not a user or not in org'
            return False
        if not user.is_active:
            print 'this would help to chain different message'
            return False
        return user

    def get_absolute_url(self):
        return reverse('users-edit', kwargs={'pk': self.pk})

class Archives(models.Model):
    machine_file_types = (
        ('ZIP', 'zip'),
        ('TAR', 'tar'),
        ('OTHER', 'OTHER')
    )


    organization =          models.ForeignKey(Organization)
    user_uploaded =         models.ForeignKey(User, null=True)
    machine_file_path =          models.CharField(max_length=100)
    machine_file_size =     models.CharField(max_length= 30)
    machine_file_upload_time = models.DateTimeField()
    machine_file_identifier = models.CharField(max_length=255,unique=True)
    machine_file_type =     models.CharField(max_length=5,choices=machine_file_types)
    bag_it_name =           models.CharField(max_length=60)
    bag_it_valid =          models.BooleanField(default=False)
    
    created_time =          models.DateTimeField(auto_now=True) # process time
    modified_time =         models.DateTimeField(auto_now_add=True)

    def bag_or_failed_name(self):
        return self.bag_it_name if self.bag_it_valid else self.machine_file_path.split('/')[-1]

    def gen_identifier(self,fname,org,date,time):
        return "{}{}{}{}".format(fname,org,date,time)
