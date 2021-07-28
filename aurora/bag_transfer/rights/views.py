from operator import itemgetter

from bag_transfer.mixins.authmixins import (ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import (BagItProfileBagInfo,
                                 BagItProfileBagInfoValues, Organization)
from bag_transfer.rights.forms import (CopyrightFormSet, LicenseFormSet,
                                       OtherFormSet, RightsForm,
                                       RightsGrantedFormSet, StatuteFormSet)
from bag_transfer.rights.models import RecordType, RightsStatement
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)


class RightsManageView(PageTitleMixin, ManagingArchivistMixin):
    """Base class for creating or updating Rights Statements."""
    template_name = "rights/manage.html"
    model = RightsStatement
    form_class = RightsForm

    def get_page_title(self, context):
        return "Edit Rights Statement" if self.kwargs.get("pk") else "Create New Rights Statement"

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.organization.pk})

    def get_formset(self, rights_basis):
        """Get the correct formset for a rights basis."""
        if rights_basis == "Copyright":
            return {"key": "copyright_form", "class": CopyrightFormSet}
        elif rights_basis == "License":
            return {"key": "license_form", "class": LicenseFormSet}
        elif rights_basis == "Statute":
            return {"key": "statute_form", "class": StatuteFormSet}
        else:
            return {"key": "other_form", "class": OtherFormSet}

    def get_applies_to_type_choices(self, organization):
        """Return applies_to_type_choices for an organization."""
        values = BagItProfileBagInfoValues.objects.filter(
            bagit_profile_baginfo__in=BagItProfileBagInfo.objects.filter(
                bagit_profile__in=organization.profile.all(),
                field="record_type"))
        applies_to_type_choices = []
        for v in values:
            record_type = RecordType.objects.get_or_create(name=v.name)[0]
            applies_to_type_choices.append((record_type.pk, record_type.name))
        return sorted(applies_to_type_choices, key=itemgetter(1))

    def save_formsets(self, form, rights_statement, organization):
        """Saves formsets associated with a rights statement."""
        formset_data = self.get_formset(rights_statement.rights_basis)
        basis_formset = formset_data["class"](self.request.POST, instance=rights_statement)
        rights_granted_formset = RightsGrantedFormSet(
            self.request.POST, instance=rights_statement)

        for formset in [rights_granted_formset, basis_formset]:
            if not formset.is_valid():
                messages.error(
                    self.request,
                    "There was a problem with your submission. Please correct the error(s) below and try again.")
                return super().form_invalid(form)

        rights_statement.save()
        rights_statement.applies_to_type.clear()
        for record_type in self.request.POST.getlist("applies_to_type"):
            rights_statement.applies_to_type.add(record_type)
        rights_statement.save()

        for formset in [rights_granted_formset, basis_formset]:
            formset.save()

        messages.success(self.request, "Rights statement saved!")
        return super().form_valid(form)


class RightsCreateView(RightsManageView, CreateView):
    """Create Rights Statements."""

    def get_context_data(self, **kwargs):
        """Adds formsets to context data."""
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(pk=self.request.GET.get("org"))
        applies_to_type_choices = self.get_applies_to_type_choices(organization)
        basis_form = RightsForm(
            applies_to_type_choices=applies_to_type_choices,
            organization=organization)
        context["copyright_form"] = CopyrightFormSet()
        context["license_form"] = LicenseFormSet()
        context["statute_form"] = StatuteFormSet()
        context["other_form"] = OtherFormSet()
        context["granted_formset"]: RightsGrantedFormSet()
        context["basis_form"] = basis_form
        context["organization"] = organization
        return context

    def form_valid(self, form):
        """Sets variables needed in formsets."""
        rights_statement = form.save(commit=False)
        organization = Organization.objects.get(pk=self.request.GET.get("org"))
        return self.save_formsets(form, rights_statement, organization)


class RightsUpdateView(RightsManageView, UpdateView):
    """Update Rights Statements."""

    def get_context_data(self, **kwargs):
        """Adds formsets to context data."""
        context = super().get_context_data(**kwargs)
        rights_statement = RightsStatement.objects.get(pk=self.kwargs.get("pk"))
        organization = rights_statement.organization
        applies_to_type_choices = self.get_applies_to_type_choices(organization)
        formset_data = self.get_formset(rights_statement.rights_basis)
        formset = formset_data["class"](instance=rights_statement)
        basis_form = RightsForm(
            applies_to_type_choices=applies_to_type_choices,
            instance=rights_statement,
            organization=organization)
        context[formset_data["key"]] = formset
        context["granted_formset"] = RightsGrantedFormSet(instance=rights_statement)
        context["basis_form"] = basis_form
        context["organization"] = organization
        return context

    def form_valid(self, form):
        """Sets variables needed in formsets."""
        rights_statement = RightsStatement.objects.get(pk=self.kwargs.get("pk"))
        organization = rights_statement.organization
        return self.save_formsets(form, rights_statement, organization)


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


class RightsDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "rights/detail.html"
    page_title = "Rights Statement"
    model = RightsStatement
