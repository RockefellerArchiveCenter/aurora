# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, generics, mixins
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from bag_transfer.models import Organization, Archives, BAGLog, BagInfoMetadata, BagItProfile, ManifestsRequired, User
from bag_transfer.mixins.authmixins import ArchivistMixin, OrgReadViewMixin
from bag_transfer.accession.models import Accession
from bag_transfer.api.serializers import *
from bag_transfer.rights.models import RightsStatement


class OrganizationViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for organizations"""
    model = Organization
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @detail_route()
    def accessions(self, request, *args, **kwargs):
        org = self.get_object()
        accessions = Accession.objects.filter(organization=org)
        serializer = AccessionSerializer(accessions, context={'request': request}, many=True)
        return Response(serializer.data)

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

    def get_serializer_class(self):
        if self.action == 'list':
            return BagItProfileListSerializer
        if self.action == 'retrieve':
            return BagItProfileSerializer
        return BagItProfileSerializer


class ArchivesViewSet(ArchivistMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Endpoint for transfers"""
    queryset = Archives.objects.all()

    def dispatch(self, *args, **kwargs):
        return super(ArchivesViewSet, self).dispatch(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ArchivesListSerializer
        if self.action == 'retrieve':
            return ArchivesSerializer
        return ArchivesSerializer


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


class AccessionViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for Accessions"""
    queryset = Accession.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AccessionListSerializer
        if self.action == 'retrieve':
            return AccessionSerializer
        return AccessionSerializer
