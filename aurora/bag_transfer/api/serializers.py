# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from bag_transfer.models import *
from bag_transfer.rights.models import *


class ExternalIdentifierSerializer(serializers.ModelSerializer):

    class Meta:
        model = AbstractExternalIdentifier
        fields = ('identifier', 'source', 'created', 'last_modified',)


class RecordCreatorsSerializer(serializers.ModelSerializer):
    external_identifiers = ExternalIdentifierSerializer(source='external_identifier', many=True)

    class Meta:
        model = RecordCreators
        fields = ('name', 'type', 'external_identifiers')


class RightsStatementRightsGrantedSerializer(serializers.ModelSerializer):
    note = serializers.StringRelatedField(source='rights_granted_note')

    class Meta:
        model = RightsStatementRightsGranted
        fields = ('act', 'start_date', 'end_date', 'note', 'restriction')


class RightsStatementSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        basis_key = obj.rights_basis.lower()
        if basis_key == 'other':
            basis_key = 'other_rights'
        rights_granted = RightsStatementRightsGrantedSerializer(
            RightsStatementRightsGranted.objects.filter(rights_statement=obj), many=True)

        if obj.rights_basis == 'Copyright':
            basis_obj = RightsStatementCopyright.objects.get(rights_statement=obj)
            basis_dict = {
                'jurisdiction': getattr(basis_obj, 'copyright_jurisdiction', ''),
                'determination_date': getattr(basis_obj, 'copyright_status_determination_date', ''),
                'status': getattr(basis_obj, 'copyright_status', ''),
            }
        elif obj.rights_basis == 'License':
            basis_obj = RightsStatementLicense.objects.get(rights_statement=obj)
            basis_dict = {
                'terms': getattr(basis_obj, 'license_terms', ''),
            }
        if obj.rights_basis == 'Statute':
            basis_obj = RightsStatementStatute.objects.get(rights_statement=obj)
            basis_dict = {
                'jurisdiction': getattr(basis_obj, 'statute_jurisdiction', ''),
                'determination_date': getattr(basis_obj, 'statute_status_determination_date', ''),
                'citation': getattr(basis_obj, 'statute_citation', ''),
            }
        if obj.rights_basis == 'Other':
            basis_obj = RightsStatementOther.objects.get(rights_statement=obj)
            basis_dict = {
                'other_rights_basis': getattr(basis_obj, 'other_rights_basis', ''),
            }
        common_dict = {
            'rights_basis': obj.rights_basis,
            'start_date': getattr(basis_obj, '{}_applicable_start_date'.format(basis_key), ''),
            'end_date': getattr(basis_obj, '{}_applicable_end_date'.format(basis_key), ''),
            'note': getattr(basis_obj, '{}_note'.format(basis_key), ''),
            'rights_granted': rights_granted.data,
        }
        common_dict.update(basis_dict)
        return common_dict


class BAGLogResultSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj


class BAGLogSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SerializerMethodField()
    summary = serializers.CharField(source='code.code_desc')
    object = serializers.HyperlinkedRelatedField(source='archive',
                                                 queryset='archive',
                                                 view_name='archives-detail')
    result = BAGLogResultSerializer(source='code.next_action')
    endTime = serializers.StringRelatedField(source='created_time')

    class Meta:
        model = BAGLog
        fields = ('url', 'type', 'summary', 'object', 'result', 'endTime',)

    def get_type(self, obj):
        if obj.code.code_type in ['BE', 'GE']:
            return "Reject"
        elif obj.code.code_type in ['I', 'S']:
            return "Accept"


class BagInfoMetadataSerializer(serializers.HyperlinkedModelSerializer):
    source_organization = serializers.StringRelatedField()
    language = serializers.StringRelatedField(many=True)
    record_creators = RecordCreatorsSerializer(many=True)

    class Meta:
        model = BagInfoMetadata
        fields = ('source_organization', 'external_identifier',
                  'title', 'record_creators', 'internal_sender_description',
                  'date_start', 'date_end', 'record_type', 'language',
                  'bag_count', 'bag_group_identifier', 'payload_oxum',
                  'bagit_profile_identifier', 'bagging_date')


class ArchivesSerializer(serializers.HyperlinkedModelSerializer):
    metadata = BagInfoMetadataSerializer()
    notifications = BAGLogSerializer(many=True)
    rights_statements = RightsStatementSerializer(many=True)
    file_size = serializers.StringRelatedField(source='machine_file_size')
    file_type = serializers.StringRelatedField(source='machine_file_type')
    identifier = serializers.StringRelatedField(source='machine_file_identifier')
    external_identifiers = ExternalIdentifierSerializer(source='external_identifier', many=True)
    parents = ExternalIdentifierSerializer(source='parent_identifier', many=True)
    collections = ExternalIdentifierSerializer(source='collection_identifier', many=True)

    class Meta:
        model = Archives
        fields = ('url', 'identifier', 'external_identifiers', 'organization',
                  'bag_it_name', 'process_status', 'file_size', 'file_type',
                  'appraisal_note', 'additional_error_info', 'metadata',
                  'rights_statements', 'parents', 'collections', 'notifications',
                  'created_time', 'modified_time')


class BagItProfileBagInfoSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        field_name = '-'.join([s[0].upper() + s[1:] for s in obj.field.split('_')])
        values = NameArraySerializer(BagItProfileBagInfoValues.objects.filter(bagit_profile_baginfo=obj), many=True).data
        return {
            field_name: {
                'required': obj.required,
                'repeatable': obj.repeatable,
                'values': values,
            }
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
        accept_bagit_version = NameArraySerializer(AcceptBagItVersion.objects.filter(bagit_profile=obj), many=True).data
        accept_serialization = NameArraySerializer(AcceptSerialization.objects.filter(bagit_profile=obj), many=True).data
        manifests_required = NameArraySerializer(ManifestsRequired.objects.filter(bagit_profile=obj), many=True).data
        tag_files_required = NameArraySerializer(TagFilesRequired.objects.filter(bagit_profile=obj), many=True).data
        tag_manifests_required = NameArraySerializer(TagManifestsRequired.objects.filter(bagit_profile=obj), many=True).data
        return {
            'BagIt-Profile-Info': {
                "Version": obj.version,
                "External-Description": obj.external_descripton,
                "Contact-Email": obj.contact_email,
                "BagIt-Profile-Identifier": obj.bagit_profile_identifier,
                "Source-Organization": obj.source_organization.name
            },
            'Bag-Info': bag_info,
            'Manifests-Required': manifests_required,
            'Allow-Fetch.txt': obj.allow_fetch,
            'Serialization': obj.serialization,
            'Accept-Serialization': accept_serialization,
            'Accept-BagIt-Version': accept_bagit_version,
            'Tag-Files-Required': tag_files_required,
            'Tag-Manifests-Required': tag_manifests_required,
        }


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    transfers = serializers.HyperlinkedIdentityField(view_name='organization-transfers')
    events = serializers.HyperlinkedIdentityField(view_name='organization-events')
    bagit_profiles = serializers.HyperlinkedIdentityField(read_only=True, view_name='organization-bagit-profiles')
    rights_statements = serializers.HyperlinkedIdentityField(read_only=True, view_name='organization-rights-statements')
    accessions = serializers.HyperlinkedIdentityField(read_only=True, view_name='organization-accessions')

    class Meta:
        model = Organization
        fields = ('url', 'id', 'is_active', 'name', 'machine_name',
                  'acquisition_type', 'accessions', 'bagit_profiles',
                  'events', 'rights_statements', 'transfers')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'is_active', 'date_joined', 'organization')


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    creators = RecordCreatorsSerializer(many=True)
    external_identifiers = ExternalIdentifierSerializer(source='external_identifier', many=True)

    class Meta:
        model = Accession
        fields = '__all__'
