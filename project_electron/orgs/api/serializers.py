# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from orgs.models import Organization, Archives, BAGLog

class ArchivesSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Archives
		fields = ('organization', 'bag_it_name', 'process_status')

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
	transfers = serializers.HyperlinkedRelatedField(many=True, view_name='archives-detail', read_only=True)

	class Meta:
		model = Organization
		fields = ('url', 'id', 'is_active', 'name', 'machine_name', 'acquisition_type', 'transfers')
