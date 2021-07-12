from decimal import Decimal

from bag_transfer.mixins.authmixins import (ArchivistMixin,
                                            ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import Archives, BagItProfile, Organization
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
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)


class OrganizationCreateView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = "orgs/create.html"
    page_title = "Add an Organization"
    model = Organization
    fields = ["name", "acquisition_type"]
    success_message = "New Organization Saved!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acquisition_types"] = Organization.ACQUISITION_TYPE_CHOICES
        return context

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "orgs/detail.html"
    page_title = "Organization Profile"
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = []
        archives = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            organization=context["object"],
        ).order_by("-created_time")[:8]
        for archive in archives:
            archive.bag_info_data = archive.bag_data
            context["uploads"].append(archive)
        context["uploads_count"] = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acquisition_types"] = Organization.ACQUISITION_TYPE_CHOICES
        return context

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationListView(PageTitleMixin, ArchivistMixin, ListView):
    template_name = "orgs/list.html"
    page_title = "Organizations"
    model = Organization


class BagItProfileManageView(PageTitleMixin, TemplateView):
    template_name = "bagit_profiles/manage.html"
    model = BagItProfile

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

    def post(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
        instance = organization.bagit_profile
        form = BagItProfileForm(request.POST, instance=instance)
        if form.is_valid():
            bagit_profile = instance if instance else form.save()
            bag_info_formset = BagItProfileBagInfoFormset(
                request.POST, instance=bagit_profile, prefix="bag_info")
            manifests_allowed_formset = ManifestsAllowedFormset(
                request.POST, instance=bagit_profile, prefix="manifests_allowed")
            manifests_formset = ManifestsRequiredFormset(
                request.POST, instance=bagit_profile, prefix="manifests")
            serialization_formset = AcceptSerializationFormset(
                request.POST, instance=bagit_profile, prefix="serialization")
            version_formset = AcceptBagItVersionFormset(
                request.POST, instance=bagit_profile, prefix="version")
            tag_manifests_formset = TagManifestsRequiredFormset(
                request.POST, instance=bagit_profile, prefix="tag_manifests")
            tag_files_formset = TagFilesRequiredFormset(
                request.POST, instance=bagit_profile, prefix="tag_files")
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
                        request,
                        "There was a problem with your submission. Please correct the error(s) below and try again.",
                    )
                    return render(
                        request,
                        self.template_name,
                        {
                            "organization": organization,
                            "form": form,
                            "bag_info_formset": bag_info_formset,
                            "manifests_allowed_formset": manifests_allowed_formset,
                            "manifests_formset": manifests_formset,
                            "serialization_formset": serialization_formset,
                            "version_formset": version_formset,
                            "tag_manifests_formset": tag_manifests_formset,
                            "tag_files_formset": tag_files_formset,
                            "meta_page_title": "BagIt Profile",
                        },
                    )
            for formset in forms_to_save:
                formset.save()
            bagit_profile.version = bagit_profile.version + Decimal(1)
            bagit_profile.bagit_profile_identifier = request.build_absolute_uri(
                reverse(
                    "bagitprofile-detail",
                    kwargs={"pk": bagit_profile.id, "format": "json"},
                )
            )
            bagit_profile.save_to_org(organization)
            messages.success(
                request,
                "BagIt Profile for {} saved".format(organization.name),
            )
            return redirect("orgs:detail", organization.pk)
        messages.error(
            request,
            "There was a problem with your submission. Please correct the error(s) below and try again.",
        )
        return render(
            request,
            self.template_name,
            {
                "form": BagItProfileForm(request.POST, instance=instance),
                "organization": Organization.objects.get(pk=self.kwargs.get("pk")),
                "bag_info_formset": BagItProfileBagInfoFormset(
                    request.POST, prefix="bag_info"),
                "manifests_allowed_formset": ManifestsAllowedFormset(
                    request.POST, prefix="manifests_allowed"),
                "manifests_formset": ManifestsRequiredFormset(
                    request.POST, prefix="manifests"),
                "serialization_formset": AcceptSerializationFormset(
                    request.POST, prefix="serialization"),
                "version_formset": AcceptBagItVersionFormset(
                    request.POST, prefix="version"),
                "tag_manifests_formset": TagManifestsRequiredFormset(
                    request.POST, prefix="tag_manifests"),
                "tag_files_formset": TagFilesRequiredFormset(
                    request.POST, prefix="tag_files"),
                "meta_page_title": "BagIt Profile",
            },
        )


class BagItProfileDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "bagit_profiles/detail.html"
    page_title = "BagIt Profile"
    model = BagItProfile

    def get_object(self):
        org = Organization.objects.get(pk=self.kwargs.get("pk"))
        return org.bagit_profile

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data["organization"] = Organization.objects.get(pk=self.kwargs.get("pk"))
        return data


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
