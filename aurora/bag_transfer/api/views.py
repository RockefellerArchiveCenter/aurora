from bag_transfer.accession.models import Accession
from bag_transfer.api.serializers import (AccessionListSerializer,
                                          AccessionSerializer,
                                          BagItProfileListSerializer,
                                          BagItProfileSerializer,
                                          BAGLogSerializer,
                                          OrganizationSerializer,
                                          RightsStatementSerializer,
                                          TransferListSerializer,
                                          TransferSerializer, UserSerializer)
from bag_transfer.lib.cleanup import CleanupRoutine
from bag_transfer.mixins.authmixins import OrgReadViewMixin
from bag_transfer.models import (BagItProfile, BAGLog, Organization, Transfer,
                                 User)
from bag_transfer.rights.models import RightsStatement
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class OrganizationViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for organizations"""

    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = Organization.objects.all()
        if not self.request.user.is_archivist():
            queryset = queryset.filter(id=self.request.user.organization.id)
        return queryset

    @action(detail=True)
    def bagit_profiles(self, request, *args, **kwargs):
        org = self.get_object()
        bagit_profiles = BagItProfile.objects.filter(organization=org)
        serializer = BagItProfileSerializer(bagit_profiles, context={"request": request}, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def rights_statements(self, request, *args, **kwargs):
        org = self.get_object()
        rights_statements = RightsStatement.objects.filter(
            transfer__isnull=True, organization=org
        )
        serializer = RightsStatementSerializer(
            rights_statements, context={"request": request}, many=True
        )
        return Response(serializer.data)


class BagItProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint for BagIt profiles"""

    queryset = BagItProfile.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return BagItProfileListSerializer
        return BagItProfileSerializer


class TransferViewSet(
    OrgReadViewMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Endpoint for transfers"""

    def dispatch(self, *args, **kwargs):
        return super(TransferViewSet, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = queryset = Transfer.objects.all()
        if not self.request.user.is_archivist():
            queryset = queryset.filter(organization=self.request.user.organization)
        process_status = self.request.GET.get("process_status", "")
        if process_status != "":
            queryset = queryset.filter(process_status=int(process_status))
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TransferListSerializer
        if self.action == "retrieve":
            return TransferSerializer
        return TransferSerializer

    def update(self, request, pk=None, *args, **kwargs):
        try:
            identifier = request.data.get("identifier")
            CleanupRoutine().run(identifier)
            return super(TransferViewSet, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)


class BAGLogViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint for events"""

    serializer_class = BAGLogSerializer

    def get_queryset(self):
        queryset = BAGLog.objects.all()
        if not self.request.user.is_archivist():
            queryset = queryset.filter(
                transfer__organization=self.request.user.organization
            )
        return queryset


class UserViewSet(OrgReadViewMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        if not self.request.user.is_archivist():
            queryset = queryset.filter(organization=self.request.user.organization)
        return queryset

    @action(detail=False)
    def current(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.pk)
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)


class AccessionViewSet(
    OrgReadViewMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Endpoint for Accessions"""

    def get_queryset(self):
        queryset = Accession.objects.all().order_by("-created")
        if not self.request.user.is_archivist():
            queryset = queryset.filter(organization=self.request.user.organization)
        process_status = self.request.GET.get("process_status", "")
        if process_status != "":
            queryset = queryset.filter(process_status=int(process_status))
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AccessionListSerializer
        if self.action == "retrieve":
            return AccessionSerializer
        return AccessionSerializer
