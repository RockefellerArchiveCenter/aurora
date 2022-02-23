from decimal import Decimal

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)

from bag_transfer.mixins.authmixins import (ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import PageTitleMixin, is_ajax
from bag_transfer.models import BagItProfile, Organization

from .form import (AcceptBagItVersionFormset, AcceptSerializationFormset,
                   BagItProfileBagInfoFormset, BagItProfileForm,
                   ManifestsAllowedFormset, ManifestsRequiredFormset,
                   TagFilesRequiredFormset, TagManifestsRequiredFormset)


class BagItProfileManageView(PageTitleMixin):
    template_name = "bagit_profiles/manage.html"
    model = BagItProfile
    form_class = BagItProfileForm

    def get_page_title(self, context):
        return "Edit BagIt Profile" if self.object else "Create BagIt Profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            form = BagItProfileForm(instance=self.object)
            organization = self.object.organization
        else:
            source_organization = self.request.user.organization
            organization = get_object_or_404(Organization, pk=self.request.GET.get("org"))
            form = BagItProfileForm(
                initial={
                    "source_organization": source_organization,
                    "contact_email": "archive@rockarch.org",
                    "organization": organization})
        context["form"] = form
        context["bag_info_formset"] = BagItProfileBagInfoFormset(instance=self.object, prefix="bag_info")
        context["manifests_allowed_formset"] = ManifestsAllowedFormset(instance=self.object, prefix="manifests_allowed")
        context["manifests_formset"] = ManifestsRequiredFormset(instance=self.object, prefix="manifests")
        context["serialization_formset"] = AcceptSerializationFormset(instance=self.object, prefix="serialization")
        context["version_formset"] = AcceptBagItVersionFormset(instance=self.object, prefix="version")
        context["tag_manifests_formset"] = TagManifestsRequiredFormset(instance=self.object, prefix="tag_manifests")
        context["tag_files_formset"] = TagFilesRequiredFormset(instance=self.object, prefix="tag_files")
        context["organization"] = organization
        return context

    def get_success_url(self):
        return reverse("bagit-profiles:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Saves associated formsets."""
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
        messages.success(self.request, "BagIt Profile saved")
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


class BagItProfileAPIAdminView(ManagingArchivistMixin, JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **kwargs):
        if not is_ajax(self.request):
            raise Http404
        resp = {"success": 0}

        if "action" in self.kwargs:
            profile = get_object_or_404(BagItProfile, pk=self.kwargs.get("pk"))
            if self.kwargs["action"] == "delete":
                profile.delete()
                resp["success"] = 1

        return self.render_to_json_response(resp, **kwargs)
