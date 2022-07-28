from uuid import uuid4

import boto3
import iso8601
from dateutil import relativedelta, tz
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from bag_transfer.lib import RAC_CMD


class Organization(models.Model):
    """Organizations are the main entities responsible for transferring records.
    They have relationships to Users, BagItProfiles and RightsStatements."""

    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=60, unique=True)
    machine_name = models.CharField(
        max_length=60, unique=True, default="orgXXX will be created here"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    ACQUISITION_TYPE_CHOICES = (
        ("donation", "Donation"),
        ("deposit", "Deposit"),
        ("transfer", "Transfer"),
    )
    acquisition_type = models.CharField(
        max_length=25, choices=ACQUISITION_TYPE_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("orgs:edit", kwargs={"pk": self.pk})

    def rights_statements(self):
        return self.rightsstatement_set.filter(transfer__isnull=True, accession__isnull=True)

    def org_users(self):
        return User.objects.filter(organization=self).order_by("username")

    def active_users(self):
        return User.objects.filter(organization=self, is_active=True)

    def inactive_users(self):
        return User.objects.filter(organization=self, is_active=False)

    def org_machine_upload_paths(self):
        """Returns a list containing the organizations' upload and processing paths."""
        root_dir = "/".join([settings.TRANSFER_UPLOADS_ROOT.rstrip("/"), self.machine_name])
        return [
            "{}/upload/".format(root_dir),
            "{}/processing/".format(root_dir),
        ]

    def save(self, *args, **kwargs):
        """Adds additional behaviors to the default save function."""
        if self.pk is None:
            """Save new Organization instances."""
            self.machine_name = "".join(c for c in self.name.lower() if c.isalnum()).rstrip()
            RAC_CMD.add_org(self.machine_name)
        else:
            orig = Organization.objects.get(pk=self.pk)
            if orig.is_active != self.is_active and not self.is_active:
                """Sets all users of org to inactive."""
                for u in self.org_users():
                    if u.is_active:
                        u.is_active = False
                        u.save()
        super(Organization, self).save(*args, **kwargs)

    @staticmethod
    def users_by_org():
        """Returns a list containing dicts of organizations and the users
        associated with them."""
        orgs = Organization.objects.all().order_by("name")
        if not orgs:
            return False
        return [{"org": org, "users": org.org_users()} for org in orgs]

    @staticmethod
    def is_org_active(org):
        """Returns an active organization object based on its machine_name,
        or None if that object does not exist."""
        try:
            org = Organization.objects.get(
                machine_name=org, is_active=True
            )
        except Organization.DoesNotExist:
            org = None
        return org


class User(AbstractUser):
    """Users can belong to one or more groups, each of which has specific permissions."""

    APPRAISER_GROUPS = ["appraisal_archivists", "managing_archivists"]
    ACCESSIONER_GROUPS = ["accessioning_archivists", "managing_archivists"]
    MANAGER_GROUPS = ["managing_archivists"]

    organization = models.ForeignKey(Organization, null=True, blank=False, on_delete=models.CASCADE, related_name="users")
    is_machine_account = models.BooleanField(default=True)
    is_org_admin = models.BooleanField(default=False)
    AbstractUser._meta.get_field("email").blank = False
    AbstractUser._meta.get_field("email")._unique = True
    AbstractUser._meta.get_field("first_name").blank = False
    AbstractUser._meta.get_field("last_name").blank = False
    AbstractUser._meta.get_field("username").blank = False
    token = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["username"]

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"pk": self.pk})

    def in_group(self, grp):
        return User.objects.filter(pk=self.pk, groups__name=grp).exists()

    def is_archivist(self):
        """Alias for `is_staff`."""
        return self.is_staff

    def has_privs(self, priv_type=None):
        """Resolves group clusters for Users."""
        if not self.is_staff:
            return False
        if self.is_superuser:
            return True
        groups = []
        if priv_type == "APPRAISER":
            groups = User.APPRAISER_GROUPS
        elif priv_type == "ACCESSIONER":
            groups = User.ACCESSIONER_GROUPS
        elif priv_type == "MANAGING":
            groups = User.MANAGER_GROUPS

        if not groups:
            return False

        return self.groups.filter(name__in=groups).exists()

    def is_manager(self):
        return self.groups.filter(name__in=User.MANAGER_GROUPS).exists()

    def permissions_by_group(self, group):
        if self.is_superuser:
            return True
        return self.groups.filter(name__in=group).exists()

    def can_appraise(self):
        return self.permissions_by_group(User.APPRAISER_GROUPS)

    def can_accession(self):
        return self.permissions_by_group(User.ACCESSIONER_GROUPS)

    def create_cognito_user(self, cognito_client):
        """Creates new user in Amazon Cognito."""
        try:
            cognito_client.admin_create_user(
                UserPoolId=settings.COGNITO_USER_POOL,
                Username=self.username,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': self.email
                    },
                ],
                DesiredDeliveryMediums=['EMAIL']
            )
        except cognito_client.exceptions.UsernameExistsException:
            # User already exists in Cognito, but we still need to create locally
            pass

    def set_cognito_user_status(self, cognito_client):
        """Enables or disables Cognito user. Creates new user if necessary."""
        try:
            cognito_user = cognito_client.admin_get_user(UserPoolId=settings.COGNITO_USER_POOL, Username=self.username)
            if cognito_user["Enabled"] != self.is_active:
                (cognito_client.admin_enable_user(UserPoolId=settings.COGNITO_USER_POOL, Username=self.username) if
                 self.is_active else cognito_client.admin_disable_user(UserPoolId=settings.COGNITO_USER_POOL, Username=self.username))
        except cognito_client.exceptions.UserNotFoundException:
            self.create_cognito_user(cognito_client)

    def create_system_user(self):
        return RAC_CMD.add_user(self.username)

    def add_user_to_system_group(self):
        return RAC_CMD.add2grp(self.organization.machine_name, self.username)

    def update_system_group(self):
        """Updates user's group if necessary."""
        orig = User.objects.get(pk=self.pk)
        if orig.organization != self.organization:
            RAC_CMD.del_from_org(self.username)
            self.add_user_to_system_group()

    def save(self, *args, **kwargs):
        """Adds additional behaviors to default save."""
        if settings.COGNITO_USE:
            """Behaviors for Cognito users."""
            cognito_client = boto3.client(
                'cognito-idp',
                aws_access_key_id=settings.COGNITO_ACCESS_KEY,
                aws_secret_access_key=settings.COGNITO_SECRET_KEY,
                region_name=settings.COGNITO_REGION)
            if self.pk is None:
                self.create_cognito_user(cognito_client)
                self.create_system_user()
                self.add_user_to_system_group()
            else:
                self.update_system_group()
                self.set_cognito_user_status(cognito_client)
        else:
            """Behaviors for local users."""
            if self.pk is None:
                if self.create_system_user():
                    if self.add_user_to_system_group():
                        self.set_password(User.objects.make_random_password())
            else:
                self.update_system_group()
        super(User, self).save(*args, **kwargs)

    def total_uploads(self):
        """Returns the number of uploads associated with a user."""
        return Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED, user_uploaded=self
        ).count()

    @staticmethod
    def is_user_active(usr, org):
        """Returns an active user object based on a username and organization,
        or None if that User does not exist."""
        try:
            user = User.objects.get(username=usr, organization=org, is_active=True)
        except User.DoesNotExist:
            user = None
        return user


class RecordCreators(models.Model):
    name = models.CharField(max_length=100)
    TYPE_CHOICES = (
        ("family", "Family"),
        ("organization", "Organization"),
        ("person", "Person"),
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class LanguageCode(models.Model):
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.code


class Transfer(models.Model):
    machine_file_types = (("ZIP", "zip"), ("TAR", "tar"), ("OTHER", "OTHER"))
    TRANSFER_STARTED = 10
    TRANSFER_COMPLETED = 20
    INVALID = 30
    VALIDATED = 40
    REJECTED = 60
    ACCEPTED = 70
    ACCESSIONING_STARTED = 80
    DELIVERED = 85
    ACCESSIONING_COMPLETE = 90
    processing_statuses = (
        (TRANSFER_STARTED, "Transfer Started"),
        (TRANSFER_COMPLETED, "Transfer Completed"),
        (INVALID, "Invalid"),
        (VALIDATED, "Validated"),
        (REJECTED, "Rejected"),
        (ACCEPTED, "Accepted"),
        (ACCESSIONING_STARTED, "Accessioning Started"),
        (DELIVERED, "In Accession Queue"),
        (ACCESSIONING_COMPLETE, "Accession Complete"),
    )

    accession = models.ForeignKey(
        "Accession", related_name="accession_transfers", null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="transfers")
    user_uploaded = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="transfers")
    machine_file_path = models.CharField(max_length=255)
    machine_file_size = models.CharField(max_length=30)
    machine_file_upload_time = models.DateTimeField()
    machine_file_identifier = models.CharField(max_length=255, unique=True)
    machine_file_type = models.CharField(max_length=5, choices=machine_file_types)
    bag_it_name = models.CharField(max_length=60)
    bag_it_valid = models.BooleanField(default=False)
    appraisal_note = models.TextField(blank=True, null=True)
    manifest = models.TextField(blank=True, null=True)
    additional_error_info = models.CharField(max_length=255, null=True, blank=True)
    process_status = models.PositiveSmallIntegerField(choices=processing_statuses, default=TRANSFER_COMPLETED)
    archivesspace_identifier = models.CharField(max_length=255, null=True, blank=True)
    archivesspace_parent_identifier = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["machine_file_upload_time"]

    def __str__(self):
        return "{}: {}".format(self.pk, self.bag_or_failed_name)

    @staticmethod
    def gen_identifier():
        """returns a unique identifier"""
        iden = str(uuid4())
        if Transfer.objects.filter(machine_file_identifier=iden).exists():
            Transfer.gen_identifier()
        return iden

    @property
    def bag_or_failed_name(self):
        """Returns a title string for the bag. Useful if you don't know whether
        or not the bag is valid."""
        if self.bag_it_valid:
            bag_info_data = self.bag_data
            return (
                "{} ({})".format(
                    bag_info_data.get("title"), bag_info_data.get("external_identifier"))
                if bag_info_data.get("external_identifier")
                else bag_info_data.get("title"))
        return self.machine_file_path.split("/")[-1]

    @property
    def errors(self):
        """Returns BagLog error objects for an Archive."""
        return None if self.bag_it_valid else [
            b for b in BAGLog.objects.filter(transfer=self, code__code_type__in=["BE", "GE"])]

    @property
    def bag_data(self):
        """Returns a dict containing bag-info.txt data for an Archive."""
        bag_data = BagInfoMetadata.objects.filter(transfer=self.pk).first()
        excluded_fields = ["id", "pk", "transfer"]
        mtm_fields = ["record_creators", "language"]
        field_names = list(set([field.name for field in BagInfoMetadata._meta.get_fields()]) - set(excluded_fields))
        values = {}
        for field_name in sorted(field_names):
            if field_name in mtm_fields:
                objects = getattr(bag_data, field_name, None)
                if objects:
                    values[field_name] = sorted([str(o) for o in objects.all()])
            else:
                field_value = getattr(bag_data, field_name, None)
                if field_value:
                    values[field_name] = getattr(bag_data, field_name, None)
        return values

    @property
    def records_creators(self):
        """Returns a list of creators associated with an Archive."""
        bag_data = BagInfoMetadata.objects.filter(transfer=self.pk).first()
        return list(bag_data.record_creators.all()) if bag_data else []

    @property
    def additional_errors(self):
        """Returns additional error information"""
        errs = []
        failures = self.failures
        if failures:
            failure_codes = [f.code.code_short for f in failures]
            if any(directory_failure in failure_codes for directory_failure in ["BZIP2", "BTAR2"]):
                errs.append("Transfer contained more than one top level directory")
            if self.additional_error_info:
                errs.append(self.additional_error_info)
        return errs

    @property
    def last_failure(self):
        """Returns the most recent bag failure"""
        return self.failures[0] if self.failures else None

    @property
    def failures(self):
        """Returns list of bag failures."""
        if self.bag_it_valid:
            return None
        error_objects = BAGLog.objects.filter(transfer=self, code__code_type__in=["BE"])
        return error_objects if error_objects else None

    @property
    def upload_time_display(self):
        return self.machine_file_upload_time.astimezone(tz.tzlocal()).strftime("%b %e, %Y %I:%M:%S %p")

    def add_autofail_information(self, obj):
        """Builds additional information for autofailed transfers."""
        if obj["auto_fail_code"] == "VIRUS":
            self.additional_error_info = "Virus found in: {}".format([k for k in obj["virus_scanresult"]][0])
        elif obj["auto_fail_code"] == "FSERR":
            self.additional_error_info = "Bag size ({}) is larger than maximum allowed size ({})".format(
                obj["file_size"], (settings.TRANSFER_FILESIZE_MAX * 1000))

    def get_or_create_mtm_objects(self, cls, model_field, field_data):
        """Gets or creates a list of objects to be saved in a many-to-many field."""
        field_as_list = field_data if isinstance(field_data, list) else [field_data.strip()]
        return [cls.objects.get_or_create(**{model_field: f})[0] for f in field_as_list]

    def save_bag_data(self, metadata):
        """Saves data from a bag-info.txt file, passed as a dict."""
        if not metadata:
            return False
        try:
            bag_data = BagInfoMetadata(
                transfer=self,
                source_organization=self.organization,
                external_identifier=metadata.get("External_Identifier", ""),
                internal_sender_description=metadata.get("Internal_Sender_Description", ""),
                title=metadata.get("Title", ""),
                date_start=iso8601.parse_date(metadata.get("Date_Start", "")),
                date_end=iso8601.parse_date(metadata.get("Date_End", "")),
                record_type=metadata.get("Record_Type", ""),
                bagging_date=iso8601.parse_date(metadata.get("Bagging_Date", "")),
                bag_count=metadata.get("Bag_Count", ""),
                bag_group_identifier=metadata.get("Bag_Group_Identifier", ""),
                payload_oxum=metadata.get("Payload_Oxum", ""),
                bagit_profile_identifier=metadata.get("BagIt_Profile_Identifier", ""))
            bag_data.save()
            creators_list = self.get_or_create_mtm_objects(RecordCreators, "name", metadata.get("Record_Creators", []))
            language_list = self.get_or_create_mtm_objects(LanguageCode, "code", metadata.get("Language", []))
            bag_data.record_creators.add(*creators_list)
            bag_data.language.add(*language_list)
            bag_data.save()
        except Exception as e:
            print("Error saving bag data: {}".format(str(e)))
            return False
        else:
            return bag_data

    def assign_rights(self):
        """Assigns rights to an Archive."""

        def update_date(obj, date_key, period_key, bag_date):
            """Updates the date if it does not exist or is not open."""
            open_key = period_key.replace("_period", "_open")
            if not(getattr(obj, date_key)):
                if hasattr(obj, open_key) and not getattr(obj, open_key):
                    period = getattr(obj, period_key) if getattr(obj, period_key) else 0
                    setattr(obj, date_key, bag_date + relativedelta.relativedelta(years=period))
                else:
                    setattr(obj, date_key, bag_date)

        try:
            bag_data = self.bag_data
            RightsStatement = apps.get_model("bag_transfer", "RightsStatement")
            RightsGranted = apps.get_model("bag_transfer", "RightsStatementRightsGranted")
            rights_statements = RightsStatement.objects.filter(
                organization=self.organization,
                applies_to_type__name=bag_data["record_type"],
                transfer__isnull=True)
            for statement in rights_statements:
                """Clone and save new rights statement."""
                rights_info = statement.rights_info
                rights_granted = RightsGranted.objects.filter(rights_statement=statement)
                statement.pk = None
                statement.transfer = self
                statement.save()

                """Assign dates to rights basis and save."""
                start_date_key, start_date_period_key, end_date_key, end_date_period_key = statement.get_date_keys(periods=True)
                for date_key, period_key, bag_data_key in [
                        (start_date_key, start_date_period_key, "date_start"),
                        (end_date_key, end_date_period_key, "date_end")]:
                    update_date(rights_info, date_key, period_key, bag_data[bag_data_key])
                rights_info.pk = None
                rights_info.rights_statement = statement
                rights_info.save()

                """Assign dates to rights granted and save."""
                for granted in rights_granted:
                    for date_key, period_key, bag_data_key in [
                            ("start_date", "start_date_period", "date_start"),
                            ("end_date", "end_date_period", "date_end")]:
                        update_date(granted, date_key, period_key, bag_data[bag_data_key])
                    granted.pk = None
                    granted.rights_statement = statement
                    granted.save()
            return True
        except Exception as e:
            print("Error saving rights statement: {}".format(str(e)))
            return False


class BAGLogCodes(models.Model):
    """
    Codes used in writing log items.

    These codes are divided into four categories:
        Bag Error - errors caused by an invalid bag, such as BagIt validation failure
        General Error - errors not specifically caused by an invalid bag, such as a virus scan connection failure
        Info - informational messages about system activity such as cron job start and end
        Success - messages indicating the successful completion of a human or machine process or activity

    Each code has a next_action field to provide information about additional system actions that have
    occurred as a result of the successful or failed process or activity.
    """

    BAGIT_VALIDATIONS = [
        "BTAR2",
        "BZIP2",
    ]
    RAC_VALIDATIONS = ["FSERR", "MDERR", "DTERR"]

    code_short = models.CharField(max_length=5)
    code_types = (
        ("BE", "Bag Error"),
        ("GE", "General Error"),
        ("I", "Info"),
        ("S", "Success"),
    )
    code_type = models.CharField(max_length=15, choices=code_types)
    code_desc = models.CharField(max_length=60)
    next_action = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{} : {}".format(self.code_short, self.code_desc)


class BAGLog(models.Model):
    """Log objects containing information about system or user actions."""

    code = models.ForeignKey(BAGLogCodes, on_delete=models.CASCADE)
    transfer = models.ForeignKey(Transfer, blank=True, null=True, on_delete=models.CASCADE, related_name="events")
    log_info = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        return "{} : {}".format(
            self.transfer.bag_or_failed_name, self.code.code_desc) if self.transfer else "-- : {}".format(self.code.code_desc)

    @classmethod
    def log_it(cls, code, transfer=None):
        """Creates BagLog object for event."""
        try:
            cls(code=BAGLogCodes.objects.get(code_short=code), transfer=transfer).save()

            if transfer:
                if code in BAGLogCodes.BAGIT_VALIDATIONS:
                    cls.log_it("GBERR", transfer)

                if code in BAGLogCodes.RAC_VALIDATIONS:
                    cls.log_it("RBERR", transfer)

            return True
        except Exception as e:
            print("Error creating BagLog: {}".format(str(e)))
        else:
            return False


class BagInfoMetadata(models.Model):
    """Metadata from a bag-info.txt file."""

    transfer = models.OneToOneField(Transfer, on_delete=models.CASCADE, related_name="metadata")
    source_organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)
    external_identifier = models.CharField(max_length=256)
    internal_sender_description = models.TextField()
    title = models.CharField(max_length=256)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    record_creators = models.ManyToManyField(RecordCreators, blank=True)
    record_type = models.CharField(max_length=256)
    language = models.ManyToManyField(LanguageCode, blank=True)
    bagging_date = models.DateTimeField()
    bag_count = models.CharField(max_length=10)
    bag_group_identifier = models.CharField(max_length=256)
    payload_oxum = models.CharField(max_length=20)
    bagit_profile_identifier = models.URLField()
    origin = models.CharField(max_length=10, default="aurora")


class BagItProfile(models.Model):
    source_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="profile")
    external_description = models.TextField(blank=True)
    version = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    bagit_profile_identifier = models.URLField(blank=True)
    contact_email = models.EmailField()
    allow_fetch = models.BooleanField(default=False)
    SERIALIZATION_CHOICES = (
        ("forbidden", "forbidden"),
        ("required", "required"),
        ("optional", "optional"),
    )
    serialization = models.CharField(
        choices=SERIALIZATION_CHOICES, max_length=25, default="optional")


class ManifestsAllowed(models.Model):
    MANIFESTS_ALLOWED_CHOICES = (("sha256", "sha256"), ("sha512", "sha512"))
    name = models.CharField(choices=MANIFESTS_ALLOWED_CHOICES, max_length=20)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="manifests_allowed")


class ManifestsRequired(models.Model):
    MANIFESTS_REQUIRED_CHOICES = (("sha256", "sha256"), ("sha512", "sha512"))
    name = models.CharField(choices=MANIFESTS_REQUIRED_CHOICES, max_length=20)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="manifests_required")


class AcceptSerialization(models.Model):
    ACCEPT_SERIALIZATION_CHOICES = (
        ("application/zip", "application/zip"),
        ("application/x-tar", "application/x-tar"),
        ("application/x-gzip", "application/x-gzip"),
    )
    name = models.CharField(choices=ACCEPT_SERIALIZATION_CHOICES, max_length=25)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="accept_serialization")


class AcceptBagItVersion(models.Model):
    BAGIT_VERSION_NAME_CHOICES = (
        ("0.96", "0.96"),
        ("0.97", "0.97"),
        ("1.0", "1.0"),
    )
    name = models.CharField(choices=BAGIT_VERSION_NAME_CHOICES, max_length=5)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="accept_bagit_version")


class TagManifestsRequired(models.Model):
    TAG_MANIFESTS_REQUIRED_CHOICES = (("sha256", "sha256"), ("sha512", "sha512"))
    name = models.CharField(choices=TAG_MANIFESTS_REQUIRED_CHOICES, max_length=20)
    bagit_profile = models.ForeignKey(
        BagItProfile, on_delete=models.CASCADE, related_name="tag_manifests_required"
    )


class TagFilesRequired(models.Model):
    name = models.CharField(max_length=256)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="tag_files_required")


class BagItProfileBagInfo(models.Model):
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="bag_info")
    FIELD_CHOICES = (
        ("bag_count", "Bag-Count"),
        ("bag_group_identifier", "Bag-Group-Identifier"),
        ("bag_size", "Bag-Size"),
        ("bagging_date", "Bagging-Date"),
        ("contact_email", "Contact-Email"),
        ("contact_name", "Contact-Name"),
        ("contact_phone", "Contact-Phone"),
        ("date_end", "Date-End"),
        ("date_start", "Date-Start"),
        ("external_description", "External-Description"),
        ("external_identifier", "External-Identifier"),
        ("internal_sender_description", "Internal-Sender-Description"),
        ("internal_sender_identifier", "Internal-Sender-Identifier"),
        ("language", "Language"),
        ("organization_address", "Organization-Address"),
        ("payload_oxum", "Payload-Oxum"),
        ("record_creators", "Record-Creators"),
        ("record_type", "Record-Type"),
        ("source_organization", "Source-Organization"),
        ("title", "Title"),
    )
    field = models.CharField(choices=FIELD_CHOICES, max_length=100)
    required = models.BooleanField(default=False, null=True)
    repeatable = models.BooleanField(default=True, null=True)


class BagItProfileBagInfoValues(models.Model):
    bagit_profile_baginfo = models.ForeignKey(BagItProfileBagInfo, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        ordering = ["name"]


class DashboardMonthData(models.Model):
    year = models.PositiveSmallIntegerField()
    month_label = models.CharField(max_length=15)
    sort_date = models.PositiveIntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    upload_count = models.PositiveSmallIntegerField(default=0)
    upload_size = models.FloatField(default=0)


class DashboardRecordTypeData(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    count = models.PositiveSmallIntegerField(default=0)
