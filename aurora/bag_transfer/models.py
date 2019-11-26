from uuid import uuid4
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from dateutil.relativedelta import relativedelta
import iso8601

from bag_transfer.lib import RAC_CMD


class Organization(models.Model):
    """Organizations are the main entities responsible for transferring records.
    They have relationships to Users, BagItProfiles and RightsStatements."""

    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=60, unique=True)
    machine_name = models.CharField(
        max_length=30, unique=True, default="orgXXX will be created here"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    ACQUISITION_TYPE_CHOICES = (
        ("donation", "Donation"),
        ("deposit", "Deposit"),
        ("transfer", "Transfer"),
    )
    acquisition_type = models.CharField(
        max_length=25, choices=ACQUISITION_TYPE_CHOICES, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("orgs:edit", kwargs={"pk": self.pk})

    def rights_statements(self):
        return self.rightsstatement_set.filter(archive__isnull=True)

    def bagit_profiles(self):
        return BagItProfile.objects.filter(applies_to_organization=self)

    def org_users(self):
        return User.objects.filter(organization=self).order_by("username")

    def active_users(self):
        return User.objects.filter(organization=self, is_active=True)

    def inactive_users(self):
        return User.objects.filter(organization=self, is_active=False)

    def org_machine_upload_paths(self):
        """Returns a list containing the organizations' upload and processing paths."""
        return [
            "{}{}/upload/".format(settings.TRANSFER_UPLOADS_ROOT, self.machine_name),
            "{}{}/processing/".format(
                settings.TRANSFER_UPLOADS_ROOT, self.machine_name
            ),
        ]

    def org_root_dir(self):
        return "%s%s".format(settings.TRANSFER_UPLOADS_ROOT, self.machine_name)

    def save(self, *args, **kwargs):
        """Adds additional behaviors to the default save function."""
        if self.pk is None:
            """Save new Organization instances."""
            self.machine_name = "".join(
                c for c in self.name.lower() if c.isalnum()
            ).rstrip()
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

    organization = models.ForeignKey(Organization, null=True, blank=False, on_delete=models.CASCADE)
    is_machine_account = models.BooleanField(default=True)
    is_org_admin = models.BooleanField(default=False)
    AbstractUser._meta.get_field("email").blank = False
    AbstractUser._meta.get_field("email")._unique = True
    AbstractUser._meta.get_field("first_name").blank = False
    AbstractUser._meta.get_field("last_name").blank = False
    AbstractUser._meta.get_field("username").blank = False

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

    def can_appraise(self):
        if self.is_superuser:
            return True
        return self.groups.filter(name__in=User.APPRAISER_GROUPS).exists()

    def can_accession(self):
        if self.is_superuser:
            return True
        return self.groups.filter(name__in=User.ACCESSIONER_GROUPS).exists()

    def save(self, *args, **kwargs):
        """Adds additional behaviors to default save."""
        if self.pk is None:
            """Sets default random password for new users."""
            if RAC_CMD.add_user(self.username):
                if RAC_CMD.add2grp(self.organization.machine_name, self.username):
                    self.set_password(User.objects.make_random_password())
                    super(User, self).save(*args, **kwargs)
        else:
            """Updates user's group if necessary."""
            orig = User.objects.get(pk=self.pk)
            if orig.organization != self.organization:
                RAC_CMD.del_from_org(self.username)
                RAC_CMD.add2grp(self.organization.machine_name, self.username)
        super(User, self).save(*args, **kwargs)

    def total_uploads(self):
        """Returns the number of uploads associated with a user."""
        return Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED, user_uploaded=self
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


class Archives(models.Model):
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
        "Accession", related_name="accession_transfers", null=True, blank=True, on_delete=models.SET_NULL
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="transfers")
    user_uploaded = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
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
    process_status = models.PositiveSmallIntegerField(
        choices=processing_statuses, default=TRANSFER_COMPLETED
    )
    archivesspace_identifier = models.CharField(max_length=255, null=True, blank=True)
    archivesspace_parent_identifier = models.CharField(
        max_length=255, null=True, blank=True
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["machine_file_upload_time"]

    def __str__(self):
        return "{}: {}".format(self.pk, self.bag_or_failed_name())

    def bag_or_failed_name(self):
        """Returns a title string for the bag. Useful if you don't know whether
        or not the bag is valid."""
        if self.bag_it_valid:
            bag_info_data = self.get_bag_data()
            return (
                "{} ({})".format(
                    bag_info_data.get("title"), bag_info_data.get("external_identifier")
                )
                if bag_info_data.get("external_identifier")
                else bag_info_data.get("title")
            )
        return self.machine_file_path.split("/")[-1]

    def rights_statements(self):
        return self.rightsstatement_set.all()

    @staticmethod
    def gen_identifier():
        """returns a unique identifier"""
        iden = str(uuid4())
        if Archives.objects.filter(machine_file_identifier=iden).exists():
            Archives.gen_identifier()
        return iden

    @classmethod
    def initial_save(
        cls,
        org,
        user,
        file_path,
        file_size,
        file_modtime,
        identifier,
        file_type,
        bag_it_name,
    ):
        """Adds default value to enable save."""
        archive = cls(
            organization=org,
            user_uploaded=user,
            machine_file_path=file_path,
            machine_file_size=file_size,
            machine_file_upload_time=file_modtime,
            machine_file_identifier=identifier,
            machine_file_type=file_type,
            bag_it_name=bag_it_name,
            process_status=cls.TRANSFER_COMPLETED,
        )
        archive.save()
        return archive

    def get_error_codes(self):
        if self.bag_it_valid:
            return ""
        return [b.code.code_desc for b in self.get_errors()]

    def get_errors(self):
        """Returns errors for an Archive."""
        if self.bag_it_valid:
            return None
        return [
            b
            for b in BAGLog.objects.filter(archive=self).exclude(
                code__code_short__in=["ASAVE", "PBAG"]
            )
        ]

    def get_bag_validations(self):
        """Returns all validations (BagIt, BagIt Profile) for an Archive."""
        if not self.bag_it_valid:
            return False
        items = BAGLog.objects.filter(
            archive=self, code__code_short__in=["PBAG", "PBAGP"]
        )
        if not items or len(items) < 2:
            return False
        data = {}
        for item in items:
            data[item.code.code_short] = item.created_time
        return data

    def get_bag_failure(self, last_only=True):
        """Returns list of bag failures."""
        if self.bag_it_valid:
            return False
        flist = [
            "BE",
        ]
        get_error_obj = BAGLog.objects.filter(archive=self, code__code_type__in=flist)
        if not get_error_obj:
            return False
        return get_error_obj[0] if last_only else get_error_obj

    def get_additional_errors(self):
        """Returns additional error information"""
        errs = []
        codes = []
        failures = self.get_bag_failure(LAST_ONLY=False)
        for fails in failures:
            codes.append(fails.code.code_short)

        if "BZIP2" in codes or "BTAR2" in codes:
            errs.append("Transfer contained more than one top level directory")

        if self.additional_error_info:
            errs.append(self.additional_error_info)
        return errs

    def get_transfer_logs(self):
        return BAGLog.objects.filter(archive=self)

    def setup_save(self, obj):
        """Builds additional info where it is required."""

        if obj["auto_fail_code"] == "VIRUS":
            # IF CONTAINS a VIRUS, BUILD additional info
            self.additional_error_info = "Virus found in: {}".format(
                [k for k in obj["virus_scanresult"]][0]
            )
        elif obj["auto_fail_code"] == "FSERR":
            self.additional_error_info = "Bag size ({}) is larger then maximum allow size ({})".format(
                obj["file_size"], (settings.TRANSFER_FILESIZE_MAX * 1000)
            )

    def save_mtm_fields(self, cls, field, model_field, metadata):
        """Handle saving of many-to-many fields."""
        obj_list = []
        if field in metadata:
            if isinstance(metadata[field], list):
                for f in metadata[field]:
                    new_obj = cls.objects.get_or_create(**{model_field: f})[0]
                    obj_list.append(new_obj)
            elif metadata[field].strip():
                new_obj = cls.objects.get_or_create(**{model_field: metadata[field]})[0]
                obj_list.append(new_obj)
        return obj_list

    def save_bag_data(self, metadata):
        """Saves data from a bag-info.txt file, passed as a dict."""
        if not metadata:
            return False

        try:
            creators_list = self.save_mtm_fields(
                RecordCreators, "Record_Creators", "name", metadata
            )
            language_list = self.save_mtm_fields(
                LanguageCode, "Language", "code", metadata
            )
            item = BagInfoMetadata(
                archive=self,
                source_organization=Organization.objects.get(
                    name=metadata["Source_Organization"]
                ),
                external_identifier=metadata.get("External_Identifier", ""),
                internal_sender_description=metadata.get(
                    "Internal_Sender_Description", ""
                ),
                title=metadata.get("Title", ""),
                date_start=iso8601.parse_date(metadata.get("Date_Start", "")),
                date_end=iso8601.parse_date(metadata.get("Date_End", "")),
                record_type=metadata.get("Record_Type", ""),
                bagging_date=iso8601.parse_date(metadata.get("Bagging_Date", "")),
                bag_count=metadata.get("Bag_Count", ""),
                bag_group_identifier=metadata.get("Bag_Group_Identifier", ""),
                payload_oxum=metadata.get("Payload_Oxum", ""),
                bagit_profile_identifier=metadata.get("BagIt_Profile_Identifier", ""),
            )
            item.save()
            for c in creators_list:
                item.record_creators.add(c)
            for l in language_list:
                item.language.add(l)
            item.save()
        except Exception as e:
            print("Error saving bag data: {}".format(str(e)))
            return False
        else:
            return True

    def get_bag_data(self):
        """Returns a dict containing bag-info.txt data for an Archive."""
        bag_data = BagInfoMetadata.objects.filter(archive=self.pk).first()
        excluded_fields = ["id", "pk", "archive"]
        mtm_fields = ["record_creators", "language"]
        field_names = [
            field.name
            for field in BagInfoMetadata._meta.get_fields()
            if field.name not in excluded_fields
        ]
        values = {}
        for field_name in sorted(field_names):
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
        """Returns a list of creators associated with an Archive."""
        bag_data = BagInfoMetadata.objects.filter(archive=self.pk).first()
        creators = []
        if bag_data:
            creators = list(bag_data.record_creators.all())
        return creators

    def assign_rights(self):
        """Assigns rights to an Archive."""
        try:
            bag_data = self.get_bag_data()
            RightsStatement = apps.get_model("bag_transfer", "RightsStatement")
            rights_statements = RightsStatement.objects.filter(
                organization=self.organization,
                applies_to_type__name=bag_data["record_type"],
                archive__isnull=True,
            )
            for statement in rights_statements:
                """Close and save new rights statement."""
                rights_info = statement.get_rights_info_object()
                rights_granted = statement.get_rights_granted_objects()
                statement.pk = None
                statement.archive = self
                statement.save()

                """Assign dates to rights basis and save."""
                if statement.rights_basis == "Other":
                    start_date_key = "other_rights_applicable_start_date"
                    end_date_key = "other_rights_applicable_end_date"
                    start_date_period_key = "other_rights_start_date_period"
                    end_date_period_key = "other_rights_end_date_period"
                else:
                    start_date_key = "{}_applicable_start_date".format(
                        statement.rights_basis.lower()
                    )
                    end_date_key = "{}_applicable_end_date".format(
                        statement.rights_basis.lower()
                    )
                    start_date_period_key = "{}_start_date_period".format(
                        statement.rights_basis.lower()
                    )
                    end_date_period_key = "{}_end_date_period".format(
                        statement.rights_basis.lower()
                    )
                if not getattr(rights_info, start_date_key):
                    if getattr(rights_info, start_date_period_key):
                        period = getattr(rights_info, start_date_period_key)
                    else:
                        period = 0
                    setattr(
                        rights_info,
                        start_date_key,
                        bag_data["date_start"] + relativedelta(years=period),
                    )
                if not getattr(rights_info, end_date_key):
                    if getattr(rights_info, end_date_period_key):
                        period = getattr(rights_info, end_date_period_key)
                    else:
                        period = 0
                    setattr(
                        rights_info,
                        end_date_key,
                        bag_data["date_end"] + relativedelta(years=period),
                    )
                rights_info.pk = None
                rights_info.rights_statement = statement
                rights_info.save()

                """Assign dates to rights granted and save."""
                for granted in rights_granted:
                    if not granted.start_date:
                        if getattr(granted, "start_date_period"):
                            period = getattr(granted, "start_date_period")
                        else:
                            period = 0
                        granted.start_date = bag_data["date_start"] + relativedelta(
                            years=period
                        )
                    if not granted.end_date:
                        if getattr(granted, "end_date_period"):
                            period = getattr(granted, "end_date_period")
                        else:
                            period = 0
                        granted.end_date = bag_data["date_end"] + relativedelta(
                            years=period
                        )
                    granted.pk = None
                    granted.rights_statement = statement
                    granted.save()
            return True
        except Exception as e:
            print("Error saving rights statement: {}".format(str(e)))
            return False
        else:
            return True


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
    archive = models.ForeignKey(Archives, blank=True, null=True, on_delete=models.CASCADE, related_name="events")
    log_info = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        val = "-- : {}".format(self.code.code_desc)
        if self.archive:
            val = "{} : {}".format(
                self.archive.bag_or_failed_name(), self.code.code_desc
            )
        return val

    @classmethod
    def log_it(cls, code, archive=None):
        """Creates BagLog object for event."""
        try:
            cls(code=BAGLogCodes.objects.get(code_short=code), archive=archive).save()

            if archive:
                if code in BAGLogCodes.BAGIT_VALIDATIONS:
                    cls.log_it("GBERR", archive)

                if code in BAGLogCodes.RAC_VALIDATIONS:
                    cls.log_it("RBERR", archive)

            return True
        except Exception as e:
            print("Error creating BagLog: {}".format(str(e)))
        else:
            return False


class BagInfoMetadata(models.Model):
    """Metadata from a bag-info.txt file."""

    archive = models.OneToOneField(Archives, on_delete=models.CASCADE, related_name="metadata")
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


class BagItProfile(models.Model):
    applies_to_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="applies_to_organization"
    )
    source_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="source_organization"
    )
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
        choices=SERIALIZATION_CHOICES, max_length=25, default="optional"
    )


class ManifestsRequired(models.Model):
    MANIFESTS_REQUIRED_CHOICES = (("sha256", "sha256"), ("md5", "md5"))
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
    )
    name = models.CharField(choices=BAGIT_VERSION_NAME_CHOICES, max_length=5)
    bagit_profile = models.ForeignKey(BagItProfile, on_delete=models.CASCADE, related_name="accept_bagit_version")


class TagManifestsRequired(models.Model):
    TAG_MANIFESTS_REQUIRED_CHOICES = (("sha256", "sha256"), ("md5", "md5"))
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
    required = models.NullBooleanField(default=False, null=True)
    repeatable = models.NullBooleanField(default=True, null=True)


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
