from decimal import Decimal

from bag_transfer.mixins.authmixins import (ArchivistMixin,
                                            ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import BagItProfile, Organization, Transfer
from bag_transfer.orgs.form import (AcceptBagItVersionFormset,
                                    AcceptSerializationFormset,
                                    BagItProfileBagInfoFormset,
                                    BagItProfileForm, ManifestsAllowedFormset,
                                    ManifestsRequiredFormset,
                                    TagFilesRequiredFormset,
                                    TagManifestsRequiredFormset)
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)


class OrganizationCreateView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = "orgs/create.html"
    page_title = "Add an Organization"
    model = Organization
    fields = ["name", "acquisition_type"]
    success_message = "New Organization Saved!"

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "orgs/detail.html"
    page_title = "Organization Profile"
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = []
        transfers = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization=context["object"],
        ).order_by("-created_time")[:8]
        for transfer in transfers:
            transfer.bag_info_data = transfer.bag_data
            context["uploads"].append(transfer)
        context["uploads_count"] = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization=context["object"],
        ).count()
        return context


class OrganizationEditView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = "orgs/update.html"
    model = Organization
    fields = ["is_active", "name", "acquisition_type"]
    success_message = "Organization Saved!"

    def get_page_title(self, context):
        return "Edit {}".format(context["object"].name)

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationListView(PageTitleMixin, ArchivistMixin, ListView):
    template_name = "orgs/list.html"
    page_title = "Organizations"
    model = Organization


class BagItProfileManageView(PageTitleMixin):
    template_name = "bagit_profiles/manage.html"
    model = BagItProfile
    form_class = BagItProfileForm

    def get_page_title(self, context):
        organization = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
        profile = organization.bagit_profile
        return "Edit BagIt Profile" if profile else "Create BagIt Profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source_organization = self.request.user.organization
        organization = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
        profile = organization.bagit_profile
        if profile:
            form = BagItProfileForm(instance=profile)
        else:
            form = BagItProfileForm(
                initial={
                    "source_organization": source_organization,
                    "contact_email": "archive@rockarch.org"})
        context["form"] = form
        context["bag_info_formset"] = BagItProfileBagInfoFormset(instance=profile, prefix="bag_info")
        context["manifests_allowed_formset"] = ManifestsAllowedFormset(instance=profile, prefix="manifests_allowed")
        context["manifests_formset"] = ManifestsRequiredFormset(instance=profile, prefix="manifests")
        context["serialization_formset"] = AcceptSerializationFormset(instance=profile, prefix="serialization")
        context["version_formset"] = AcceptBagItVersionFormset(instance=profile, prefix="version")
        context["tag_manifests_formset"] = TagManifestsRequiredFormset(instance=profile, prefix="tag_manifests")
        context["tag_files_formset"] = TagFilesRequiredFormset(instance=profile, prefix="tag_files")
        context["organization"] = organization
        return context

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.kwargs.get("pk")})

    def form_valid(self, form):
        """Saves associated formsets."""
        organization = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
        bagit_profile = form.save()
        bag_info_formset = BagItProfileBagInfoFormset(
            self.request.POST, instance=bagit_profile, prefix="bag_info")
        manifests_allowed_formset = ManifestsAllowedFormset(
            self.request.POST, instance=bagit_profile, prefix="manifests_allowed")
        manifests_formset = ManifestsRequiredFormset(
            self.request.POST, instance=bagit_profile, prefix="manifests")
        serialization_formset = AcceptSerializationFormset(
            self.request.POST, instance=bagit_profile, prefix="serialization")
        version_formset = AcceptBagItVersionFormset(
            self.request.POST, instance=bagit_profile, prefix="version")
        tag_manifests_formset = TagManifestsRequiredFormset(
            self.request.POST, instance=bagit_profile, prefix="tag_manifests")
        tag_files_formset = TagFilesRequiredFormset(
            self.request.POST, instance=bagit_profile, prefix="tag_files")
        forms_to_save = [
            bag_info_formset,
            manifests_allowed_formset,
            manifests_formset,
            serialization_formset,
            version_formset,
            tag_manifests_formset,
            tag_files_formset,
        ]
        for formset in forms_to_save:
            if not formset.is_valid():
                messages.error(
                    self.request,
                    "There was a problem with your submission. Please correct the error(s) below and try again.")
                return super().form_invalid(form)
            else:
                formset.save()
        bagit_profile.version = bagit_profile.version + Decimal(1)
        bagit_profile.bagit_profile_identifier = self.request.build_absolute_uri(
            reverse(
                "bagitprofile-detail",
                kwargs={"pk": bagit_profile.id, "format": "json"},
            )
        )
        bagit_profile.save_to_org(organization)
        messages.success(
            self.request,
            "BagIt Profile for {} saved".format(organization.name))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "There was a problem with your submission. Please correct the error(s) below and try again.")
        return super().form_invalid(form)


class BagItProfileCreateView(BagItProfileManageView, CreateView):
    pass


class BagItProfileUpdateView(BagItProfileManageView, UpdateView):
    pass


class BagItProfileDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "bagit_profiles/detail.html"
    page_title = "BagIt Profile"
    model = BagItProfile

    def get_object(self):
        org = Organization.objects.get(pk=self.kwargs.get("pk"))
        return org.bagit_profile


class BagItProfileAPIAdminView(ManagingArchivistMixin, JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        resp = {"success": 0}

        if "action" in self.kwargs:
            organization = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
            if self.kwargs["action"] == "delete":
                organization.bagit_profile.delete()
                resp["success"] = 1

        return self.render_to_json_response(resp, **kwargs)
