# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata

class BAGLogResultSerializer(serializers.Serializer):
	name = serializers.SerializerMethodField()

	def get_name(self, obj):
		# TODO: Would be better to implement this in model
		accept_codes = ['CSTR', 'CEND', 'ASAVE', 'APASS', 'PBAG', 'PBAGP', 'BACPT', 'BACC']
		if obj not in accept_codes:
			return "Transfer deleted"
		elif obj == 'ASAVE':
			return "Staged for validation"
		elif obj == 'APASS':
			return "Staged for appraisal"
		elif obj == 'PBAG':
			return "Staged for conformance to local specifications"
		elif obj == 'PBAGP':
			return "Staged for appraisal"
		elif obj == 'BACPT':
			return "Staged for accessioning"
		elif obj == 'BACC':
			return "Staged for ingest"

class BAGLogSerializer(serializers.HyperlinkedModelSerializer):
	type = serializers.SerializerMethodField()
	summary = serializers.SerializerMethodField()
	object = serializers.SerializerMethodField()
	result = BAGLogResultSerializer(source='code.code_short')
	endTime = serializers.StringRelatedField(source='created_time')

	class Meta:
		model = BAGLog
		fields = ('url', 'type', 'summary', 'object', 'result', 'endTime',)

	def get_type(self, obj):
		code = obj.code.code_short
		# TODO: This seems super buggy and problematic; should probably look at the types on the error codes
		accept_codes = ['CSTR', 'CEND', 'ASAVE', 'APASS', 'PBAG', 'PBAGP', 'BACPT', 'BACC']
		if code in accept_codes:
			return "Accept"
		else:
			return "Reject"

	def get_summary(self, obj):
		return obj.code.code_desc

	def get_object(self, obj):
		try:
			return obj.archive.bag_it_name
		except:
			return None

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
					'bagit_profile_identifier', 'bagging_date',)

class ArchivesSerializer(serializers.HyperlinkedModelSerializer):
	metadata = BagInfoMetadataSerializer(many=True)
	notifications = BAGLogSerializer(many=True)

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
