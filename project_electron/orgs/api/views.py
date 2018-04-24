# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata, BagItProfile, ManifestsRequired, User
from orgs.mixins.authmixins import ArchivistMixin, OrgReadViewMixin
from orgs.api.serializers import OrganizationSerializer, ArchivesSerializer, BAGLogSerializer, BagInfoMetadataSerializer, BagItProfileSerializer, UserSerializer, RightsStatementSerializer
from orgs.rights.models import RightsStatement


class OrganizationViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for organizations"""
    model = Organization
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @detail_route()
    def bagit_profiles(self, request, *args, **kwargs):
        org = self.get_object()
        bagit_profiles = BagItProfile.objects.filter(applies_to_organization=org)
        serializer = BagItProfileSerializer(bagit_profiles, context={'request': request}, many=True)
        return Response(serializer.data)

    @detail_route(url_path='bagit_profiles/(?P<number>[0-9]+)')
    def bagit_profiles_detail(self, request, number=None, *args, **kwargs):
        org = self.get_object()
        bagit_profile = BagItProfile.objects.get(id=number)
        serializer = BagItProfileSerializer(bagit_profile, context={'request': request})
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

    @detail_route()
    def rights_statements(self, request, *args, **kwargs):
        org = self.get_object()
        rights_statements = RightsStatement.objects.filter(archive__isnull=True, organization=org)
        serializer = RightsStatementSerializer(rights_statements, context={'request': request}, many=True)
        return Response(serializer.data)


class BagItProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint for BagIt profiles"""
    model = BagItProfile
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


class UserViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route()
    def current(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
