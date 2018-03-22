# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata, BagItProfile, ManifestsRequired
from orgs.authmixins import ArchivistMixin, OrgReadViewMixin
from orgs.api.serializers import OrganizationSerializer, ArchivesSerializer, BAGLogSerializer, BagInfoMetadataSerializer, BagItProfileSerializer


class OrganizationViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for organizations"""
    model = Organization
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @detail_route()
    def bagit_profiles(self, request, *args, **kwargs):
        org = self.get_object()
        bagit_profiles = BagItProfile.objects.filter(organization=org).order_by('-created_time')
        manifests_required = ManifestsRequired.objects
        page = self.paginate_queryset(bagit_profiles)
        if page is not None:
            serializer = BagItProfileSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


    @detail_route()
    def transfers(self, request, *args, **kwargs):
        org = self.get_object()
        transfers = Archives.objects.filter(organization=org).order_by('-created_time')
        page = self.paginate_queryset(transfers)
        if page is not None:
            serializer = ArchivesSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


    @detail_route()
    def events(self, request, *args, **kwargs):
        org = self.get_object()
        archives = Archives.objects.filter(organization=org)
        notifications = BAGLog.objects.filter(archive__in=archives).order_by('-created_time')
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = BAGLogSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class BagItProfileViewSet(ArchivistMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for BagIt profiles"""
    queryset = BagItProfile.objects.all()
    serializer_class = BagItProfileSerializer

class ArchivesViewSet(ArchivistMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for transfers"""
    queryset = Archives.objects.all()
    serializer_class = ArchivesSerializer

class BAGLogViewSet(ArchivistMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for events"""
    queryset = BAGLog.objects.all()
    serializer_class = BAGLogSerializer
