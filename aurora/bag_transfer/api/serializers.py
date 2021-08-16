from bag_transfer.accession.models import Accession
from bag_transfer.models import (AcceptBagItVersion, AcceptSerialization,
                                 BagInfoMetadata, BagItProfile,
                                 BagItProfileBagInfo,
                                 BagItProfileBagInfoValues, BAGLog,
                                 ManifestsAllowed, ManifestsRequired,
                                 Organization, RecordCreators,
                                 TagFilesRequired, TagManifestsRequired,
                                 Transfer, User)
from bag_transfer.rights.models import (RightsStatement,
                                        RightsStatementCopyright,
                                        RightsStatementLicense,
                                        RightsStatementOther,
                                        RightsStatementRightsGranted,
                                        RightsStatementStatute)
from rest_framework import serializers


class RecordCreatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordCreators
        fields = (
            "name",
            "type",
        )


class RightsStatementRightsGrantedSerializer(serializers.ModelSerializer):
    note = serializers.StringRelatedField(source="rights_granted_note")
    end_date = serializers.SerializerMethodField()
    grant_restriction = serializers.CharField(source="restriction")

    def get_end_date(self, obj):
        end_date = obj.end_date
        if not end_date:
            end_date = "open" if obj.end_date_open else None
        return end_date

    class Meta:
        model = RightsStatementRightsGranted
        fields = ("act", "start_date", "end_date", "note", "grant_restriction")


class RightsStatementSerializer(serializers.ModelSerializer):
    rights_granted = RightsStatementRightsGrantedSerializer(many=True)
    rights_basis = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    basis_note = serializers.SerializerMethodField()
    jurisdiction = serializers.SerializerMethodField(allow_null=True, required=False)
    determination_date = serializers.SerializerMethodField(allow_null=True, required=False)
    copyright_status = serializers.SerializerMethodField(allow_null=True, required=False)
    terms = serializers.SerializerMethodField(allow_null=True, required=False)
    statute_citation = serializers.SerializerMethodField(allow_null=True, required=False)
    other_basis = serializers.SerializerMethodField(
        allow_null=True, required=False
    )

    class Meta:
        model = RightsStatement
        fields = (
            "rights_basis",
            "determination_date",
            "jurisdiction",
            "start_date",
            "end_date",
            "basis_note",
            "copyright_status",
            "terms",
            "statute_citation",
            "other_basis",
            "rights_granted",
        )

    def get_rights_basis(self, obj):
        return obj.rights_basis.lower()

    def get_basis_obj(self, obj):
        if obj.rights_basis == "Copyright":
            return RightsStatementCopyright.objects.get(rights_statement=obj)
        elif obj.rights_basis == "License":
            return RightsStatementLicense.objects.get(rights_statement=obj)
        elif obj.rights_basis == "Statute":
            return RightsStatementStatute.objects.get(rights_statement=obj)
        elif obj.rights_basis == "Other":
            return RightsStatementOther.objects.get(rights_statement=obj)

    def get_basis_key(self, obj):
        return (
            "other_rights"
            if (obj.rights_basis.lower() == "other")
            else obj.rights_basis.lower()
        )

    def get_start_date(self, obj):
        return getattr(
            self.get_basis_obj(obj),
            "{}_applicable_start_date".format(self.get_basis_key(obj)),
        )

    def get_end_date(self, obj):
        end_date = getattr(
            self.get_basis_obj(obj),
            "{}_applicable_end_date".format(self.get_basis_key(obj)),
        )
        if not end_date:
            end_date = (
                "open" if "{}_end_date_open".format(self.get_basis_key(obj)) else None
            )
        return end_date

    def get_basis_note(self, obj):
        return getattr(
            self.get_basis_obj(obj), "{}_note".format(self.get_basis_key(obj))
        )

    def get_jurisdiction(self, obj):
        return (
            getattr(
                self.get_basis_obj(obj),
                "{}_jurisdiction".format(self.get_basis_key(obj)),
            )
            if (obj.rights_basis in ["Copyright", "Statute"])
            else None
        )

    def get_determination_date(self, obj):
        if obj.rights_basis == "Copyright":
            return getattr(
                self.get_basis_obj(obj), "copyright_status_determination_date"
            )
        elif obj.rights_basis == "Statute":
            return getattr(self.get_basis_obj(obj), "statute_determination_date")
        else:
            return None

    def get_copyright_status(self, obj):
        return (
            getattr(self.get_basis_obj(obj), "copyright_status")
            if (obj.rights_basis == "Copyright")
            else None
        )

    def get_terms(self, obj):
        return (
            getattr(self.get_basis_obj(obj), "license_terms")
            if (obj.rights_basis == "License")
            else None
        )

    def get_statute_citation(self, obj):
        return (
            getattr(self.get_basis_obj(obj), "statute_citation")
            if (obj.rights_basis == "Statute")
            else None
        )

    def get_other_basis(self, obj):
        return (
            getattr(self.get_basis_obj(obj), "other_rights_basis").lower()
            if (obj.rights_basis == "Other")
            else None
        )


class BAGLogResultSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj


class BAGLogSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SerializerMethodField()
    summary = serializers.CharField(source="code.code_desc")
    object = serializers.HyperlinkedRelatedField(
        source="transfer", view_name="transfer-detail", read_only=True
    )
    result = BAGLogResultSerializer(source="code.next_action")
    endTime = serializers.StringRelatedField(source="created_time")

    class Meta:
        model = BAGLog
        fields = ("url", "type", "summary", "object", "result", "endTime")

    def get_type(self, obj):
        if obj.code.code_type in ["BE", "GE"]:
            return "Reject"
        elif obj.code.code_type in ["I", "S"]:
            return "Accept"


class BagInfoMetadataSerializer(serializers.HyperlinkedModelSerializer):
    source_organization = serializers.StringRelatedField()
    language = serializers.StringRelatedField(many=True, read_only=True)
    record_creators = RecordCreatorsSerializer(many=True)

    class Meta:
        model = BagInfoMetadata
        fields = (
            "source_organization",
            "title",
            "record_creators",
            "internal_sender_description",
            "date_start",
            "date_end",
            "record_type",
            "language",
            "bag_count",
            "bag_group_identifier",
            "payload_oxum",
            "bagit_profile_identifier",
            "bagging_date",
            "origin",
        )


class TransferSerializer(serializers.HyperlinkedModelSerializer):
    metadata = BagInfoMetadataSerializer(read_only=True)
    events = BAGLogSerializer(many=True, read_only=True)
    rights_statements = RightsStatementSerializer(many=True, read_only=True)
    file_size = serializers.StringRelatedField(source="machine_file_size")
    file_type = serializers.StringRelatedField(source="machine_file_type")
    identifier = serializers.StringRelatedField(source="machine_file_identifier")
    origin = serializers.StringRelatedField(source="metadata.origin")

    class Meta:
        model = Transfer
        fields = (
            "url",
            "identifier",
            "organization",
            "origin",
            "bag_it_name",
            "process_status",
            "file_size",
            "file_type",
            "appraisal_note",
            "additional_error_info",
            "metadata",
            "rights_statements",
            "events",
            "archivesspace_identifier",
            "archivesspace_parent_identifier",
            "created_time",
            "modified_time",
        )


class TransferListSerializer(serializers.HyperlinkedModelSerializer):
    identifier = serializers.StringRelatedField(source="machine_file_identifier")

    class Meta:
        model = Transfer
        fields = ("url", "identifier", "created_time", "modified_time")


class BagItProfileBagInfoSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        field_name = "-".join([s[0].upper() + s[1:] for s in obj.field.split("_")])
        if len(BagItProfileBagInfoValues.objects.filter(bagit_profile_baginfo=obj)) > 0:
            values = NameArraySerializer(
                BagItProfileBagInfoValues.objects.filter(bagit_profile_baginfo=obj),
                many=True,
            ).data
            return {
                field_name: {
                    "required": obj.required,
                    "repeatable": obj.repeatable,
                    "values": values,
                }
            }
        else:
            return {
                field_name: {"required": obj.required, "repeatable": obj.repeatable}
            }


class NameArraySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return obj.name


class BagItProfileSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        bag_info = {}
        bag_info_values = BagItProfileBagInfo.objects.filter(bagit_profile=obj)
        for bi in bag_info_values:
            bag_info.update(BagItProfileBagInfoSerializer(bi).data)
        accept_bagit_version = NameArraySerializer(
            AcceptBagItVersion.objects.filter(bagit_profile=obj), many=True
        ).data
        accept_serialization = NameArraySerializer(
            AcceptSerialization.objects.filter(bagit_profile=obj), many=True
        ).data
        manifests_allowed = NameArraySerializer(
            ManifestsAllowed.objects.filter(bagit_profile=obj), many=True
        ).data
        manifests_required = NameArraySerializer(
            ManifestsRequired.objects.filter(bagit_profile=obj), many=True
        ).data
        tag_files_required = NameArraySerializer(
            TagFilesRequired.objects.filter(bagit_profile=obj), many=True
        ).data
        tag_manifests_required = NameArraySerializer(
            TagManifestsRequired.objects.filter(bagit_profile=obj), many=True
        ).data
        return {
            "BagIt-Profile-Info": {
                "Version": obj.version,
                "External-Description": obj.external_description,
                "Contact-Email": obj.contact_email,
                "BagIt-Profile-Identifier": obj.bagit_profile_identifier,
                "Source-Organization": obj.source_organization.name,
            },
            "Bag-Info": bag_info,
            "Manifests-Allowed": manifests_allowed,
            "Manifests-Required": manifests_required,
            "Allow-Fetch.txt": obj.allow_fetch,
            "Serialization": obj.serialization,
            "Accept-Serialization": accept_serialization,
            "Accept-BagIt-Version": accept_bagit_version,
            "Tag-Files-Required": tag_files_required,
            "Tag-Manifests-Required": tag_manifests_required,
        }


class BagItProfileListSerializer(serializers.HyperlinkedModelSerializer):
    organization = serializers.StringRelatedField(source="profile_organization")

    class Meta:
        model = BagItProfile
        fields = ("url", "external_description", "version", "organization")


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    rights_statements = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="organization-rights-statements")
    bagit_profiles = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="organization-bagit-profiles")

    class Meta:
        model = Organization
        fields = (
            "url",
            "id",
            "is_active",
            "name",
            "machine_name",
            "acquisition_type",
            "bagit_profiles",
            "rights_statements",
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "url",
            "username",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "organization",
        )


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    creators = RecordCreatorsSerializer(many=True, read_only=True)
    transfers = TransferListSerializer(
        source="accession_transfers", many=True, read_only=True
    )
    organization = serializers.StringRelatedField(read_only=True)
    rights_statements = RightsStatementSerializer(many=True, read_only=True)
    language = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Accession
        fields = "__all__"


class AccessionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Accession
        fields = ("url", "title", "accession_number", "created", "last_modified")
