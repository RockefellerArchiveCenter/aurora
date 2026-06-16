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

from .form import BagItProfileBagInfoFormset, BagItProfileForm


class BagItProfileManageView(PageTitleMixin):
    template_name = "bagit_profiles/manage.html"
    model = BagItProfile
    form_class = BagItProfileForm

    def get_organization(self):
        if self.object:
            return self.object.organization
        else:
            return get_object_or_404(Organization, pk=self.request.GET.get("org"))

    def get_page_title(self, context):
        org = self.get_organization()
        if self.object:
            return "Edit BagIt Profile: {}".format(org)
        else:
            return "Create BagIt Profile: {}".format(org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_organization()
        if self.object:
            form = BagItProfileForm(instance=self.object)
        else:
            source_organization = self.request.user.organization
            form = BagItProfileForm(
                initial={
                    "source_organization": source_organization,
                    "contact_email": "archive@rockarch.org",
                    "organization": organization})
        context["form"] = form
        context["bag_info_formset"] = BagItProfileBagInfoFormset(instance=self.object, prefix="bag_info")
        context["organization"] = organization
        return context

    def get_success_url(self):
        return reverse("bagit-profiles:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Saves associated formsets."""
        bagit_profile = form.save()
        bag_info_formset = BagItProfileBagInfoFormset(
            self.request.POST, instance=bagit_profile, prefix="bag_info")
        if not bag_info_formset.is_valid():
            error_messages = []
            for form in bag_info_formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

            for error in bag_info_formset.non_form_errors():
                error_messages.append(f"Form error: {error}")

            detailed_errors = "; ".join(error_messages)

            messages.error(
                self.request,
                f"There was a problem with your submission: {detailed_errors} "
                "Please correct the error(s) and try again."
            )
            return super().form_invalid(form)
        else:
            bag_info_formset.save()
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
        detailed_errors = "; ".join(
            [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        )
        messages.error(
            self.request,
            f"There was a problem with your submission: {detailed_errors} "
            "Please correct the error(s) below and try again."
        )
        return super().form_invalid(form)


class BagItProfileCreateView(BagItProfileManageView, CreateView):
    pass


class BagItProfileUpdateView(BagItProfileManageView, UpdateView):
    pass


class BagItProfileDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "bagit_profiles/detail.html"
    model = BagItProfile

    def get_page_title(self, context):
        return "BagIt Profile: {}".format(context["object"].organization)


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
