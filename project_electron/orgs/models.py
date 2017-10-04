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
    def active_users(self):
        return User.objects.filter(organization=self,is_active=True)
    def inactive_users(self):
        return User.objects.filter(organization=self,is_active=False)

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
        else:

            # SET USERS INACTIVE WHEN ORG IS SET TO INACTIVE
            orig = Organization.objects.get(pk=self.pk)
            if orig.is_active != self.is_active and not self.is_active:
                # what if ORG is RAC
                for u in self.org_users():
                    if u.is_active:
                        u.is_active = False
                        u.save()
                        print 'USER {} set to inactive!'.format(u.username)

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

    class Meta:
        ordering = ['name']

class User(AbstractUser):

    organization = models.ForeignKey(Organization, null=True, blank=False)
    is_machine_account = models.BooleanField(default=True)

    from_ldap = models.BooleanField(editable=False, default=False)
    is_new_account = models.BooleanField(default=False)

    AbstractUser._meta.get_field('email').blank = False

    def in_group(self,GRP):
        return User.objects.filter(pk=self.pk, groups_name=GRP).exists()

    def save(self, *args, **kwargs):

        if self.pk is None:

            pass
        else:

            if self.from_ldap:
                orig = User.objects.get(pk=self.pk)
                if orig.organization != self.organization:
                    if RAC_CMD.del_from_org(self.username):
                        if RAC_CMD.add2grp(self.organization.machine_name,self.username):
                                print 'GROUP CHANGED'

                    ## SHOULD ACTUALLY REMOVE ANY GROUPS THAT MATCH REGEX ORGXXX
                    if orig.organization:
                        pass
                        # remove from ORG
                        # if RAC_CMD.del_from_org(self.username,orig.organization.machine_name):

                        #     if RAC_CMD.add2grp(self.organization.machine_name,self.username):
                        #         print 'GROUP CHANGED'
                    else:
                        if RAC_CMD.add2grp(self.organization.machine_name,self.username):
                            print 'GROUP CHANGED'

                        # FIRST TIME an ORG is added this will set account to not new
                        if self.is_new_account:
                            self.is_new_account = False

        if self.username[:2] == "va":
            if not self.is_staff:
                self.is_staff = True
                print 'SET to RAC USER!'


        super(User,self).save(*args,**kwargs)

    def total_uploads(self):
        return Archives.objects.filter(user_uploaded=self).count()

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

                        
                        ## should AUTO SET TO RAC
                        if uid[:2] == "va":
                            primary_org = Organization.objects.filter(pk=1)
                            if primary_org:
                                new_user.organization = primary_org[0]
                                print 'USER AUTO ADDED TO PRIMARY ORG'


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
        return reverse('users-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['username']

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
