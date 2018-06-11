# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from bag_transfer.lib import RAC_CMD
from bag_transfer.lib.ldap_auth import LDAP_Manager


class Organization(models.Model):
    is_active =     models.BooleanField(default=True)
    name =          models.CharField(max_length=60, unique=True)
    machine_name =  models.CharField(max_length=30, unique=True, default="orgXXX will be created here")
    created_time =  models.DateTimeField(auto_now = True)
    modified_time = models.DateTimeField(auto_now_add = True)
    ACQUISITION_TYPE_CHOICES = (
        ('donation', 'Donation'),
        ('deposit', 'Deposit'),
        ('transfer', 'Transfer'),
    )
    acquisition_type = models.CharField(max_length=25, choices=ACQUISITION_TYPE_CHOICES, null=True, blank=True)

    def rights_statements(self):
        return self.rightsstatement_set.filter(archive__isnull=True)

    def bagit_profiles(self):
        return BagItProfile.objects.filter(applies_to_organization=self)

    def org_users(self):
        return User.objects.filter(organization=self).order_by('username')
    def active_users(self):
        return User.objects.filter(organization=self,is_active=True)
    def inactive_users(self):
        return User.objects.filter(organization=self,is_active=False)

    def org_root_dir(self):
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

    def org_machine_upload_paths(self):
        return [
            '{}{}/upload/'.format(settings.TRANSFER_UPLOADS_ROOT, self.machine_name),
            '{}{}/processing/'.format(settings.TRANSFER_UPLOADS_ROOT, self.machine_name)
        ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('orgs-edit', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']

class User(AbstractUser):

    appraiser_groups = [u"appraisal_archivists", u"managing_archivists"]
    accessioner_groups = [u"accessioning_archivists", u"managing_archivists"]
    managing_group = [u"managing_archivists"]

    organization =          models.ForeignKey(Organization, null=True, blank=False)
    is_machine_account =    models.BooleanField(default=True)
    from_ldap =             models.BooleanField(default=False)
    is_new_account =        models.BooleanField(default=False)
    is_org_admin =          models.BooleanField(default=False)

    AbstractUser._meta.get_field('email').blank = False
    AbstractUser._meta.get_field('first_name').blank = False
    AbstractUser._meta.get_field('last_name').blank = False

    def in_group(self,GRP):
        return User.objects.filter(pk=self.pk, groups__name=GRP).exists()

    def is_archivist(self):
        """friendlier way to check if staff"""
        return self.is_staff

    def has_privs(self, priv_type=None):
        """resolves group clusters for user object"""
        if not self.is_staff:
            return False
        if self.is_superuser:
            return True
        groups = []
        if priv_type == 'APPRAISER':
            groups = User.appraiser_groups
        elif priv_type == 'ACCESSIONER':
            groups = User.accessioner_groups
        elif priv_type == 'MANAGING':
            groups = User.managing_group

        if not groups: return False

        return self.groups.filter(name__in=groups).exists()


    def is_manager(self):
        return self.groups.filter(name='managing_archivists').exists()

    def can_appraise(self):
        return self.groups.filter(name__in=['appraisal_archivists', 'managing_archivists']).exists()

    def check_password_ldap(self, password):
        from bag_transfer.mixins.ldap_mixin import _LDAPUserExtension
        ldap_interface = _LDAPUserExtension()
        if ldap_interface.authenticate(username=self.username, password=password):
            return True
        return False

    def set_password_ldap(self, raw_password):
        from bag_transfer.mixins.ldap_mixin import _LDAPUserExtension
        ldap_interface = _LDAPUserExtension()
        if ldap_interface.set_password(username=self.username,password=raw_password):
            self.password = make_password(raw_password)
            self._password = raw_password
            return True
        return False


    def save(self, *args, **kwargs):

        if self.pk is None:
            # All ldap account creation should follow a standard, since the app doesn't have username in form
            if self.from_ldap:
                ldap_auth = LDAP_Manager()
                new_username = ldap_auth.create_user(self.organization.machine_name, self.email,self.get_full_name(),self.last_name)
                if not new_username:
                    ## raise exception here and hook into message chain
                    return
                else:
                    self.username = new_username
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
        return Archives.objects.filter(process_status__gte=20, user_uploaded=self).count()

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
                            primary_org = Organization.objects.all().order_by('pk')
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

class RecordCreators(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class LanguageCode(models.Model):
    code = models.CharField(max_length=3)

    def __unicode__(self):
        return self.code

class Archives(models.Model):
    machine_file_types = (
        ('ZIP', 'zip'),
        ('TAR', 'tar'),
        ('OTHER', 'OTHER')
    )
    processing_statuses = (
        (10, 'Transfer Started'),
        (20, 'Transfer Completed'),
        (30, 'Invalid'),
        (40, 'Validated'),
        (60, 'Rejected'),
        (70, 'Accepted'),
        (75, 'Accessioning Started'),
        (90, 'Accession Complete')
    )

    organization =          models.ForeignKey(Organization, related_name="transfers")
    user_uploaded =         models.ForeignKey(User, null=True)
    machine_file_path =     models.CharField(max_length=100)
    machine_file_size =     models.CharField(max_length= 30)
    machine_file_upload_time = models.DateTimeField()
    machine_file_identifier = models.CharField(max_length=255,unique=True)
    machine_file_type =     models.CharField(max_length=5,choices=machine_file_types)
    bag_it_name =           models.CharField(max_length=60)
    bag_it_valid =          models.BooleanField(default=False)
    appraisal_note =        models.TextField(blank=True, null=True)

    additional_error_info = models.CharField(max_length=255,null=True,blank=True)
    process_status =        models.PositiveSmallIntegerField(choices=processing_statuses,default=20)
    created_time =          models.DateTimeField(auto_now=True) # process time
    modified_time =         models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{}: {}'.format(self.pk, self.bag_or_failed_name())

    def bag_or_failed_name(self):
        return self.bag_it_name if self.bag_it_valid else self.machine_file_path.split('/')[-1]

    def rights_statements(self):
        return self.rightsstatement_set.all()

    @staticmethod
    def gen_identifier(fname,org,date,time):
        """returns an identifier if doesn't exists already, Else False"""
        iden = "{}{}{}{}".format(fname,org,date,time)
        return (False if Archives.objects.filter(machine_file_identifier = iden) else iden)

    @classmethod
    def initial_save(cls, org, user, file_path, file_size, file_modtime, identifier,file_type, bag_it_name):
        archive = cls(
            organization =          org,
            user_uploaded =         user,
            machine_file_path =     file_path,
            machine_file_size =     file_size,
            machine_file_upload_time =  file_modtime,
            machine_file_identifier =   identifier,
            machine_file_type       =   file_type,
            bag_it_name =               bag_it_name,
            process_status = 20
        )
        archive.save()
        return archive
    def get_error_codes(self):
        if self.bag_it_valid:
            return ''
        return [b.code.code_desc for b in self.get_errors()]

    def get_errors(self):
        if self.bag_it_valid:
            return None
        return [b for b in BAGLog.objects.filter(archive=self).exclude(code__code_short__in=['ASAVE','PBAG'])]


    def get_bag_validations(self):
        if not self.bag_it_valid:
            return False
        items = BAGLog.objects.filter(archive=self,code__code_short__in=['PBAG','PBAGP'])
        if not items or len(items) < 2:
            return False
        data = {}
        for item in items:
            data[item.code.code_short] = item.created_time
        return data

    def get_bag_failure(self, LAST_ONLY = True):
        if self.bag_it_valid:
            return False
        flist = ['BE',]
        get_error_obj = BAGLog.objects.filter(archive=self,code__code_type__in=flist)
        if not get_error_obj:
            return False
        return get_error_obj[0] if LAST_ONLY else get_error_obj

    def get_additional_errors(self):
        errs = []
        codes = []
        failures = self.get_bag_failure(LAST_ONLY=False)
        for fails in failures:
            codes.append(fails.code.code_short)

        if 'BZIP2' in codes or 'BTAR2' in codes:
            errs.append('Transfer contained more than one top level directory')

        if self.additional_error_info:
            errs.append(self.additional_error_info)
        return errs

    def get_transfer_logs(self):
        return BAGLog.objects.filter(archive=self)

    def setup_save(self, obj):
        """Builds additional info where more info is required than ecode short"""

        if obj['auto_fail_code'] == 'VIRUS':
            # IF CONTAINS a VIRUS, BUILD additional info
            self.additional_error_info = 'Virus found in: {}'.format([k for k in obj['virus_scanresult']][0])
        elif obj['auto_fail_code'] == 'FSERR':
            self.additional_error_info = 'Bag size ({}) is larger then maximum allow size ({})'.format(obj['file_size'], (settings.TRANSFER_FILESIZE_MAX * 1000))

    def save_mtm_fields(self, cls, field, model_field, metadata):
        obj_list = []
        if field in metadata:
            if type(metadata[field]) is list:
                for f in metadata[field]:
                    new_obj = cls.objects.get_or_create(**{model_field: f})[0]
                    obj_list.append(new_obj)
            else:
                new_obj = cls.objects.get_or_create(**{model_field: metadata[field]})[0]
                obj_list.append(new_obj)
        return obj_list

    def save_bag_data(self, metadata):
        if not metadata:
            return False

        try:
            creators_list = self.save_mtm_fields(RecordCreators, 'Record_Creators', 'name', metadata)
            language_list = self.save_mtm_fields(LanguageCode, 'Language', 'code', metadata)
            item = BagInfoMetadata(
                archive = self,
                source_organization = Organization.objects.get(name=metadata['Source_Organization']),
                external_identifier = metadata.get('External_Identifier', ''),
                internal_sender_description = metadata.get('Internal_Sender_Description', ''),
                title = metadata.get('Title', ''),
                date_start = metadata.get('Date_Start', ''),
                date_end = metadata.get('Date_End', ''),
                record_type = metadata.get('Record_Type', ''),
                bagging_date = metadata.get('Bagging_Date', ''),
                bag_count = metadata.get('Bag_Count', ''),
                bag_group_identifier = metadata.get('Bag_Group_Identifier', ''),
                payload_oxum = metadata.get('Payload_Oxum', ''),
                bagit_profile_identifier = metadata.get('BagIt_Profile_Identifier', '')
            )
            item.save()
            for c in creators_list:
                item.record_creators.add(c)
            for l in language_list:
                item.language.add(l)
            item.save()
        except Exception as e:
            print e
            return False
        else:
            return True # this at least assumes nothing blew up

    def get_bag_data(self):
        bag_data = BagInfoMetadata.objects.filter(archive=self.pk).first()
        excluded_fields = ['id', 'pk', 'archive']
        mtm_fields = ['record_creators', 'language']
        field_names = [field.name for field in BagInfoMetadata._meta.get_fields() if field.name not in excluded_fields]
        values = {}
        for field_name in field_names:
            if field_name in mtm_fields:
                strings = []
                objects = getattr(bag_data, field_name, None)
                if objects:
                    for creator in objects.all():
                        strings.append(str(creator))
                    values[field_name] = sorted(strings)
            else:
                field_value = getattr(bag_data, field_name, None)
                if field_value:
                    values[field_name] = getattr(bag_data, field_name, None)
        return values

    def get_records_creators(self):
        bag_data = BagInfoMetadata.objects.filter(archive=self.pk).first()
        if bag_data:
            return list(bag_data.record_creators.all())
        else:
            return []

    def assign_rights(self):
        try:
            bag_data = self.get_bag_data()
            RightsStatement = apps.get_model('bag_transfer', 'RightsStatement')
            rights_statements = RightsStatement.objects.filter(organization=self.organization, applies_to_type__name=bag_data['record_type'], archive__isnull=True)
            for statement in rights_statements:
                rights_info = statement.get_rights_info_object()
                rights_granted = statement.get_rights_granted_objects()
                # Clone and save rights statement
                statement.pk = None
                statement.archive = self
                statement.save()
                # Assign dates to rights basis and save
                if statement.rights_basis == 'Other':
                    start_date_key = 'other_rights_applicable_start_date'
                    end_date_key = 'other_rights_applicable_end_date'
                    start_date_period_key = 'other_rights_start_date_period'
                    end_date_period_key = 'other_rights_end_date_period'
                else:
                    start_date_key = '{}_applicable_start_date'.format(statement.rights_basis.lower())
                    end_date_key = '{}_applicable_end_date'.format(statement.rights_basis.lower())
                    start_date_period_key = '{}_start_date_period'.format(statement.rights_basis.lower())
                    end_date_period_key = '{}_end_date_period'.format(statement.rights_basis.lower())
                if not getattr(rights_info, start_date_key):
                    if getattr(rights_info, start_date_period_key):
                        period = getattr(rights_info, start_date_period_key)
                    else:
                        period = 0
                    setattr(rights_info, start_date_key, bag_data['date_start'] + relativedelta(years=period))
                if not getattr(rights_info, end_date_key):
                    if getattr(rights_info, end_date_period_key):
                        period = getattr(rights_info, end_date_period_key)
                    else:
                        period = 0
                    setattr(rights_info, end_date_key, bag_data['date_end'] + relativedelta(years=period))
                rights_info.pk = None
                rights_info.rights_statement = statement
                rights_info.save()
                # Assign dates to rights granted and save
                for granted in rights_granted:
                    if not granted.start_date:
                        if getattr(granted, 'start_date_period'):
                            period = getattr(granted, 'start_date_period')
                        else:
                            period = 0
                        granted.start_date = bag_data['date_start'] + relativedelta(years=period)
                    if not granted.end_date:
                        if getattr(granted, 'end_date_period'):
                            period = getattr(granted, 'end_date_period')
                        else:
                            period = 0
                        granted.end_date = bag_data['date_end'] + relativedelta(years=period)
                    granted.pk = None
                    granted.rights_statement = statement
                    granted.save()
            return True
        except Exception as e:
            print e
            return False
        else:
            return True

    class Meta:
        ordering = ['machine_file_upload_time']

class BAGLogCodes(models.Model):
    """
    Codes used in writing logs items.

    These codes are divided into four categories:
        Bag Error - errors caused by an invalid bag, such as BagIt validation failure
        General Error - errors not specifically caused by an invalid bag, such as a virus scan connection failure
        Info - informational messages about system activity such as cron job start and end
        Success - messages indicating the successful completion of a human or machine process or activity

    Each code has a next_action field to provide information about additional system actions that have
    occurred as a result of the successful or failed process or activity.
    """
    eCat_bagit_validation = ['BTAR2','BZIP2',]
    eCat_rac_profile = ['FSERR','MDERR','DTERR']

    code_short = models.CharField(max_length=5)
    code_types = (
        ('BE', 'Bag Error'),
        ('GE', 'General Error'),
        ('I', 'Info'),
        ('S', 'Success'),
    )
    code_type = models.CharField(max_length=15, choices=code_types)
    code_desc = models.CharField(max_length=60)
    next_action = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return "{} : {}".format(self.code_short,self.code_desc)

class BAGLog(models.Model):
    code = models.ForeignKey(BAGLogCodes)
    archive = models.ForeignKey(Archives, blank=True,null=True, related_name='notifications')
    log_info = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        val = "-- : {}".format(self.code.code_desc)
        if self.archive:
            val = "{} : {}".format( self.archive.bag_or_failed_name(), self.code.code_desc)
        return val

    @classmethod
    def log_it(cls, code, archive = None):
        try:
            print code
            item = cls(
                code = BAGLogCodes.objects.get(code_short=code),
                archive = archive
            ).save()


            if archive:
                if code in BAGLogCodes.eCat_bagit_validation:
                    cls.log_it('GBERR',archive)

                if code in BAGLogCodes.eCat_rac_profile:
                    cls.log_it('RBERR',archive)

            return True
        except Exception as e:
            print e
        else:
            return False

    class Meta:
        ordering = ['-created_time']

class BagInfoMetadata(models.Model):
    archive =                       models.OneToOneField(Archives, related_name='metadata')
    source_organization =           models.ForeignKey(Organization, blank=True,null=True,)
    external_identifier =           models.CharField(max_length=256)
    internal_sender_description =   models.TextField()
    title =                         models.CharField(max_length=256)
    date_start =                    models.DateTimeField()
    date_end =                      models.DateTimeField()
    record_creators =               models.ManyToManyField(RecordCreators, blank=True)
    record_type =                   models.CharField(max_length=30)
    language =                      models.ManyToManyField(LanguageCode, blank=True)
    bagging_date =                  models.DateTimeField()
    bag_count =                     models.CharField(max_length=10)
    bag_group_identifier =          models.CharField(max_length=256)
    payload_oxum =                  models.CharField(max_length=20)
    bagit_profile_identifier =      models.URLField()

class BagItProfile(models.Model):
    applies_to_organization = models.ForeignKey(Organization, related_name='applies_to_organization')
    source_organization = models.ForeignKey(Organization, related_name='source_organization')
    external_descripton = models.TextField(blank=True)
    version = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    bagit_profile_identifier = models.URLField(blank=True)
    contact_email = models.EmailField()
    allow_fetch = models.BooleanField(default=False)
    SERIALIZATION_CHOICES = (
        ('forbidden', 'forbidden'),
        ('required', 'required'),
        ('optional', 'optional'),
    )
    serialization = models.CharField(choices=SERIALIZATION_CHOICES, max_length=25, default='optional')

class ManifestsRequired(models.Model):
    MANIFESTS_REQUIRED_CHOICES = (
        ('sha256', 'sha256'),
        ('md5', 'md5')
    )
    name = models.CharField(choices=MANIFESTS_REQUIRED_CHOICES, max_length=20)
    bagit_profile = models.ForeignKey(BagItProfile, related_name='manifests_required')

class AcceptSerialization(models.Model):
    ACCEPT_SERIALIZATION_CHOICES = (
        ('application/zip', 'application/zip'),
        ('application/x-tar', 'application/x-tar'),
        ('application/x-gzip', 'application/x-gzip'),
    )
    name = models.CharField(choices=ACCEPT_SERIALIZATION_CHOICES, max_length=25)
    bagit_profile = models.ForeignKey(BagItProfile, related_name='accept_serialization')

class AcceptBagItVersion(models.Model):
    BAGIT_VERSION_NAME_CHOICES = (
        ('0.96', '0.96'),
        ('0.97', '0.97'),
    )
    name = models.CharField(choices=BAGIT_VERSION_NAME_CHOICES, max_length=5)
    bagit_profile = models.ForeignKey(BagItProfile)

class TagManifestsRequired(models.Model):
    TAG_MANIFESTS_REQUIRED_CHOICES = (
        ('sha256', 'sha256'),
        ('md5', 'md5')
    )
    name = models.CharField(choices=TAG_MANIFESTS_REQUIRED_CHOICES, max_length=20)
    bagit_profile = models.ForeignKey(BagItProfile)

class TagFilesRequired(models.Model):
    name = models.CharField(max_length=256)
    bagit_profile = models.ForeignKey(BagItProfile)

class BagItProfileBagInfo(models.Model):
    bagit_profile = models.ForeignKey(BagItProfile)
    FIELD_CHOICES = (
        ('source_organization', 'Source-Organization'),
        ('organization_address', 'Organization-Address'),
        ('contact_name', 'Contact-Name'),
        ('contact_phone', 'Contact-Phone'),
        ('contact_email', 'Contact-Email'),
        ('external_descripton', 'External-Description'),
        ('external_identifier', 'External-Identifier'),
        ('internal_sender_description', 'Internal-Sender-Description'),
        ('internal_sender_identifier', 'Internal-Sender-Identifier'),
        ('title', 'Title'),
        ('date_start', 'Date-Start'),
        ('date_end', 'Date-End'),
        ('record_creators', 'Record-Creators'),
        ('record_type', 'Record-Type'),
        ('language', 'Language'),
        ('bagging_date', 'Bagging-Date'),
        ('bag_group_identifier', 'Bag-Group-Identifier'),
        ('bag_count', 'Bag-Count'),
        ('bag_size', 'Bag-Size'),
        ('payload_oxum', 'Payload-Oxum'),
    )
    field = models.CharField(choices=FIELD_CHOICES, max_length=100)
    required = models.NullBooleanField(default=False, null=True)
    repeatable = models.NullBooleanField(default=True, null=True)

class BagItProfileBagInfoValues(models.Model):
    bagit_profile_baginfo = models.ForeignKey(BagItProfileBagInfo)
    name = models.CharField(max_length=256)