from django.http import Http404
from django.contrib import messages
from django.views.generic import CreateView, DetailView, TemplateView
from django.shortcuts import render, redirect, get_object_or_404

from bag_transfer.models import (
    BagItProfile,
    BagItProfileBagInfo,
    BagItProfileBagInfoValues,
    Organization,
)
from bag_transfer.rights.models import RecordType, RightsStatement
from bag_transfer.rights.forms import CopyrightFormSet, LicenseFormSet, StatuteFormSet, OtherFormSet, RightsGrantedFormSet, RightsForm
from bag_transfer.mixins.authmixins import ManagingArchivistMixin, OrgReadViewMixin
from bag_transfer.mixins.formatmixins import JSONResponseMixin


class RightsManageView(ManagingArchivistMixin, CreateView):
    template_name = "rights/manage.html"
    model = RightsStatement
    form_class = RightsForm

    def get_formset(self, rights_basis):
        if rights_basis == "Copyright":
            return {"key": "copyright_form", "class": CopyrightFormSet}
        elif rights_basis == "License":
            return {"key": "license_form", "class": LicenseFormSet}
        elif rights_basis == "Statute":
            return {"key": "statute_form", "class": StatuteFormSet}
        else:
            return {"key": "other_form", "class": OtherFormSet}

    def get_applies_to_type_choices(self, organization):
        values = BagItProfileBagInfoValues.objects.filter(
            bagit_profile_baginfo__in=BagItProfileBagInfo.objects.filter(
                bagit_profile__in=BagItProfile.objects.filter(
                    applies_to_organization=organization
                ),
                field="record_type",
            )
        )
        applies_to_type_choices = []
        for v in values:
            record_type = RecordType.objects.get_or_create(name=v.name)[0]
            applies_to_type_choices.append((record_type.pk, record_type.name))
        return sorted(applies_to_type_choices, key=lambda tup: tup[1])

    def get(self, request, *args, **kwargs):
        if self.kwargs.get("pk"):
            rights_statement = RightsStatement.objects.get(pk=self.kwargs.get("pk"))
            organization = rights_statement.organization
            applies_to_type_choices = self.get_applies_to_type_choices(organization)
            formset_data = self.get_formset(rights_statement.rights_basis)
            formset = formset_data["class"](instance=rights_statement)
            basis_form = RightsForm(
                applies_to_type_choices=applies_to_type_choices,
                instance=rights_statement,
                organization=organization,
            )
            granted_formset = RightsGrantedFormSet(instance=rights_statement)
            return render(
                request,
                self.template_name,
                {
                    "organization": organization,
                    formset_data["key"]: formset,
                    "basis_form": basis_form,
                    "granted_formset": granted_formset,
                },
            )
        else:
            organization = Organization.objects.get(pk=self.request.GET.get("org"))
            applies_to_type_choices = self.get_applies_to_type_choices(organization)
            basis_form = RightsForm(
                applies_to_type_choices=applies_to_type_choices,
                organization=organization,
            )
            return render(
                request,
                self.template_name,
                {
                    "copyright_form": CopyrightFormSet(),
                    "license_form": LicenseFormSet(),
                    "statute_form": StatuteFormSet(),
                    "other_form": OtherFormSet(),
                    "organization": organization,
                    "basis_form": basis_form,
                    "granted_formset": RightsGrantedFormSet(),
                },
            )

    def post(self, request, *args, **kwargs):
        applies_to_type = request.POST.getlist("applies_to_type")

        if not self.kwargs.get("pk"):
            organization = Organization.objects.get(pk=self.request.GET.get("org"))
            applies_to_type_choices = self.get_applies_to_type_choices(organization)
            form = RightsForm(
                request.POST,
                applies_to_type_choices=applies_to_type_choices,
                organization=organization,
            )
            if not form.is_valid():
                messages.error(
                    request,
                    "There was a problem with your submission. Please correct the error(s) below and try again.",
                )
                return render(
                    request,
                    self.template_name,
                    {
                        "copyright_form": CopyrightFormSet(),
                        "license_form": LicenseFormSet(),
                        "statute_form": StatuteFormSet(),
                        "other_form": OtherFormSet(),
                        "organization": organization,
                        "basis_form": form,
                    },
                )
            rights_statement = form.save(commit=False)
        else:
            rights_statement = RightsStatement.objects.get(pk=self.kwargs.get("pk"))
            organization = rights_statement.organization
            applies_to_type_choices = self.get_applies_to_type_choices(organization)

        formset_data = self.get_formset(rights_statement.rights_basis)
        basis_formset = formset_data["class"](request.POST, instance=rights_statement)
        rights_granted_formset = RightsGrantedFormSet(
            request.POST, instance=rights_statement
        )

        for formset in [rights_granted_formset, basis_formset]:
            if not formset.is_valid():
                messages.error(
                    request,
                    "There was a problem with your submission. Please correct the error(s) below and try again.",
                )
                form = RightsForm(
                    request.POST,
                    applies_to_type_choices=applies_to_type_choices,
                    organization=organization,
                )
                return render(
                    request,
                    self.template_name,
                    {
                        formset_data["key"]: formset_data["class"](request.POST),
                        "organization": organization,
                        "basis_form": form,
                        "granted_formset": rights_granted_formset,
                    },
                )

        rights_statement.save()
        rights_statement.applies_to_type.clear()
        for record_type in applies_to_type:
            rights_statement.applies_to_type.add(record_type)
        rights_statement.save()

        for formset in [rights_granted_formset, basis_formset]:
            formset.save()

        messages.success(request, "Rights statement saved!")
        return redirect("orgs:detail", organization.pk)


class RightsAPIAdminView(ManagingArchivistMixin, JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        resp = {"success": 0}

        if "action" in self.kwargs:
            obj = get_object_or_404(RightsStatement, pk=context["pk"])
            if self.kwargs["action"] == "delete":
                obj.delete()
                resp["success"] = 1

        return self.render_to_json_response(resp, **kwargs)


class RightsDetailView(OrgReadViewMixin, DetailView):
    template_name = "rights/detail.html"
    model = RightsStatement

    def get_context_data(self, *args, **kwargs):
        context = super(RightsDetailView, self).get_context_data(**kwargs)
        context["meta_page_title"] = "{} PREMIS rights statement".format(
            self.object.organization
        )
        context["rights_basis_info"] = self.object.get_rights_info_object
        context["rights_granted_info"] = self.object.get_rights_granted_objects
        return context
