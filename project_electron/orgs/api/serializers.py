# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata, BagItProfile, BagItProfileBagInfo, BagItProfileBagInfoValues, ManifestsRequired, TagFilesRequired, TagManifestsRequired, AcceptSerialization, AcceptBagItVersion, User


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
        elif obj.code.code_type in ['S']:
            return "Accept"


class BagInfoMetadataSerializer(serializers.HyperlinkedModelSerializer):
    source_organization = serializers.StringRelatedField()
    language = serializers.StringRelatedField(many=True)
    record_creators = serializers.StringRelatedField(many=True)

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
    file_size = serializers.StringRelatedField(source='machine_file_size')
    file_type = serializers.StringRelatedField(source='machine_file_type')

    class Meta:
        model = Archives
        fields = ('url', 'organization', 'bag_it_name', 'process_status',
                  'file_size', 'file_type', 'appraisal_note',
                  'additional_error_info', 'metadata', 'notifications',
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
                "BagIt-Profile-Identifier": obj.bagit_profile_identifier
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

    class Meta:
        model = Organization
        fields = ('url', 'id', 'is_active', 'name', 'machine_name',
                  'acquisition_type', 'bagit_profiles', 'transfers', 'events')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'is_active', 'date_joined', 'organization')
