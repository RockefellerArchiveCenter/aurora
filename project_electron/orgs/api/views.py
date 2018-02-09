# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from orgs.models import Organization, Archives, BAGLog, BagInfoMetadata
from orgs.api.serializers import OrganizationSerializer, ArchivesSerializer, BAGLogSerializer, BagInfoMetadataSerializer

class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @detail_route()
    def transfers(self, request, *args, **kwargs):
        org = self.get_object()
        transfers = Archives.objects.filter(organization=org).order_by('-created_time')
        page = self.paginate_queryset(transfers)
        if page is not None:
            serializer = ArchivesSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

        return Response(transfer_json.data)

    @detail_route()
    def notifications(self, request, *args, **kwargs):
        org = self.get_object()
        archives = Archives.objects.filter(organization=org)
        notifications = BAGLog.objects.filter(archive__in=archives).order_by('-created_time')
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = BAGLogSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class ArchivesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Archives.objects.all()
    serializer_class = ArchivesSerializer

    @detail_route()
    def notifications(self, request, *args, **kwargs):
        archive = self.get_object()
        notifications = BAGLog.objects.filter(archive=archive).order_by('created_time')
        notifications_json = BAGLogSerializer(notifications, context={'request': request}, many=True)
        return Response(notifications_json.data)

    @detail_route()
    def metadata(self, request, *args, **kwargs):
        archive = self.get_object()
        metadata = BagInfoMetadata.objects.filter(archive=archive)
        metadata_json = BagInfoMetadataSerializer(metadata, context={'request': request}, many=True)
        return Response(metadata_json.data)

class BAGLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BAGLog.objects.all()
    serializer_class = BAGLogSerializer
