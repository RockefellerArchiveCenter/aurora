# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata

class BAGLogSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = BAGLog
		fields = ('code', 'archive', 'log_info')

class BagInfoMetadataSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = BagInfoMetadata
		fields = '__all__'

class ArchivesSerializer(serializers.HyperlinkedModelSerializer):
	notifications = serializers.HyperlinkedIdentityField(view_name='archives-notifications')
	metadata = serializers.HyperlinkedIdentityField(view_name='archives-metadata')

	class Meta:
		model = Archives
		fields = ('organization', 'bag_it_name', 'process_status', 'metadata', 'notifications')

		@list_route()
	    def notifications(self, request, *args, **kwargs):
	        org = self.get_object()
			notifications = BAGLog.objects.filter(organization=org).order_by('created_time')
			notifications_json = BAGLogSerializer(notifications, many=True)
	        return Response(notifications_json.data)

		@list_route()
	    def metadata(self, request, *args, **kwargs):
	        org = self.get_object()
			metadata = BagInfoMetadata.objects.get(source_organization=org)
			metadata_json = BAGLogSerializer(notifications, many=True)
	        return Response(metadata_json.data)

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
	transfers = serializers.HyperlinkedIdentityField(view_name='organization-transfers')

	class Meta:
		model = Organization
		fields = ('url', 'id', 'is_active', 'name', 'machine_name', 'acquisition_type', 'transfers')

	@list_route()
    def transfers(self, request, *args, **kwargs):
        org = self.get_object()
		transfers = Archives.objects.filter(organization=org).order_by('-created_time')
		transfer_json = ArchivesSerializer(transfers, many=True)
        return Response(transfer_json.data)
