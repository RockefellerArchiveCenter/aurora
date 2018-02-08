# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from orgs.models import Organization, Archives, BAGLog
from orgs.api.serializers import OrganizationSerializer, ArchivesSerializer, BAGLogSerializer

class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class ArchivesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Archives.objects.all()
    serializer_class = ArchivesSerializer

class BAGLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BAGLog.objects.all()
    serializer_class = BAGLogSerializer
