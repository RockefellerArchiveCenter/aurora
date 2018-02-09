# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata

class BAGLogSerializer(serializers.HyperlinkedModelSerializer):
	code = serializers.StringRelatedField()

	class Meta:
		model = BAGLog
		fields = ('url', 'code', 'archive', 'log_info', 'created_time')

class BagInfoMetadataSerializer(serializers.HyperlinkedModelSerializer):
	source_organization = serializers.StringRelatedField()
	language = serializers.StringRelatedField(many=True)
	record_creators = serializers.StringRelatedField(many=True)

	class Meta:
		model = BagInfoMetadata
		fields = ('url', 'source_organization', 'external_identifier',
					'title', 'record_creators', 'internal_sender_description',
					'date_start', 'date_end', 'record_type', 'language',
					'bag_count', 'bag_group_identifier', 'payload_oxum',
					'bagit_profile_identifier', 'bagging_date',)

class ArchivesSerializer(serializers.HyperlinkedModelSerializer):
	metadata = serializers.HyperlinkedIdentityField(view_name='archives-metadata')
	notifications = serializers.HyperlinkedIdentityField(view_name='archives-notifications')

	class Meta:
		model = Archives
		fields = ('url', 'organization', 'bag_it_name', 'process_status', 'machine_file_size',
		'machine_file_upload_time', 'machine_file_identifier', 'machine_file_type',
		'created_time', 'modified_time', 'appraisal_note', 'additional_error_info',
		'metadata', 'notifications',)

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
	transfers = serializers.HyperlinkedIdentityField(view_name='organization-transfers')
	notifications = serializers.HyperlinkedIdentityField(view_name='organization-notifications')

	class Meta:
		model = Organization
		fields = ('url', 'id', 'is_active', 'name', 'machine_name', 'acquisition_type', 'transfers', 'notifications')
