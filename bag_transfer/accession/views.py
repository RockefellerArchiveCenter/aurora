import json

import requests
from dateutil import tz
from django.contrib import messages
from django.db.models import CharField, F
from django.db.models.functions import Concat
from django.shortcuts import reverse
from django.views.generic import CreateView, DetailView, ListView

from aurora import settings
from bag_transfer.accession.db_functions import GroupConcat
from bag_transfer.accession.forms import AccessionForm, CreatorsFormSet
from bag_transfer.accession.models import Accession
from bag_transfer.api.serializers import AccessionSerializer
from bag_transfer.lib.clients import ArchivesSpaceClient
from bag_transfer.lib.view_helpers import file_size
from bag_transfer.mixins.authmixins import (AccessioningArchivistMixin,
                                            ArchivistMixin)
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import (BaseDatatableView, PageTitleMixin,
                                            is_ajax)
from bag_transfer.models import BAGLog, LanguageCode, RecordCreators, Transfer
from bag_transfer.rights.models import RightsStatement


class AccessionView(PageTitleMixin, ArchivistMixin, JSONResponseMixin, ListView):
    template_name = "accession/main.html"
    page_title = "Accessioning Queue"
    model = Accession

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = Transfer.objects.filter(process_status=Transfer.ACCEPTED).annotate(
            transfer_group=Concat(
                "organization",
                "metadata__record_type",
                GroupConcat("metadata__record_creators"),
                output_field=CharField(),
            )
        ).order_by("transfer_group")
        context["accessions"] = Accession.objects.all()
        context["deliver"] = True if settings.DELIVERY_URL else False
        return context

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            return self.handle_ajax_request(request)
        return super().get(self, request, *args, **kwargs)

    def handle_ajax_request(self, request):
        """Handles JavaScript AJAX requests."""
        rdata = {}
        rdata["success"] = 0
        if request.user.has_privs("ACCESSIONER"):
            if "accession_id" in request.GET:
                try:
                    accession = Accession.objects.get(pk=request.GET["accession_id"])
                    accession_data = AccessionSerializer(
                        accession, context={"request": request}
                    )
                    resp = requests.post(
                        settings.DELIVERY_URL,
                        data=json.dumps(
                            accession_data.data, indent=4, sort_keys=True, default=str
                        ),
                        headers={
                            "Content-Type": "application/json",
                            "apikey": settings.DELIVERY_API_KEY,
                        },
                    )
                    resp.raise_for_status()
                    accession.process_status = Accession.DELIVERED
                    accession.save()
                    rdata["success"] = 1
                except Exception as e:
                    rdata["error"] = str(e)
        return self.render_to_json_response(rdata)


class AccessionDetailView(PageTitleMixin, AccessioningArchivistMixin, DetailView):
    template_name = "accession/detail.html"
    model = Accession

    def get_page_title(self, context):
        return context["object"].title


class AccessionCreateView(PageTitleMixin, AccessioningArchivistMixin, JSONResponseMixin, CreateView):
    template_name = "accession/create.html"
    page_title = "Create Accession Record"
    model = Accession
    form_class = AccessionForm

    def get_success_url(self):
        return reverse("accession:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Saves associated formsets and delivers accession data."""
        creators_formset = CreatorsFormSet(self.request.POST)
        id_list = list(map(int, self.request.GET.get("transfers").split(",")))
        transfers_list = Transfer.objects.filter(pk__in=id_list)
        rights_statements = (
            RightsStatement.objects.filter(transfer__in=id_list)
            .annotate(rights_group=F("rights_basis"))
            .order_by("rights_group"))
        if creators_formset.is_valid():
            form.process_status = Accession.CREATED
            accession = form.save()
            creators_formset.save()
            self.update_accession_rights(RightsStatement.merge_rights(rights_statements), accession)
            self.update_accession_transfers(transfers_list, accession)
            messages.success(self.request, "Accession created successfully!")
            if settings.DELIVERY_URL:
                try:
                    accession_data = AccessionSerializer(
                        accession, context={"request": self.request})
                    resp = requests.post(
                        settings.DELIVERY_URL,
                        data=json.dumps(accession_data.data, default=str),
                        headers={
                            "Content-Type": "application/json",
                            "apikey": settings.DELIVERY_API_KEY,
                        },
                    )
                    resp.raise_for_status()
                    accession.process_status = Accession.DELIVERED
                    accession.save()
                    messages.success(self.request, "Accession data delivered.")
                except Exception as e:
                    messages.error(self.request, "Error delivering accession data: {}".format(e))
            return super().form_valid(form)
        messages.error(
            self.request,
            "There was a problem with your submission. Please correct the error(s) below and try again.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_list = list(map(int, self.request.GET.get("transfers").split(",")))
        transfers_list = Transfer.objects.filter(pk__in=id_list)
        rights_statements = (
            RightsStatement.objects.filter(transfer__in=id_list)
            .annotate(rights_group=F("rights_basis"))
            .order_by("rights_group"))
        organization = transfers_list[0].organization
        creators_list = list(set([c for t in transfers_list for c in t.records_creators]))
        notes, dates, descriptions_list, languages_list, extent_files, extent_size, record_type = self.grouped_transfer_data(transfers_list)
        notes.update(self.rights_statement_notes(rights_statements))
        language = self.parse_language(languages_list)
        title = self.parse_title(
            organization,
            record_type,
            ", ".join([creator.name for creator in creators_list]))
        context["form"] = AccessionForm(
            initial={
                "title": title,
                "start_date": sorted(dates.get("start", []))[0],
                "end_date": sorted(dates.get("end", []))[-1],
                "description": " ".join(set(descriptions_list)),
                "extent_files": extent_files,
                "extent_size": extent_size,
                "access_restrictions": " ".join(
                    set(notes.get("other", []) + notes.get("license", []) + notes.get("statute", []))
                ),
                "use_restrictions": " ".join(set(notes.get("copyright", []))),
                "acquisition_type": organization.acquisition_type,
                "appraisal_note": " ".join(set(notes.get("appraisal", []))),
                "organization": organization,
                "language": language,
                "creators": creators_list,
            }
        )
        context["creators_formset"] = CreatorsFormSet(queryset=RecordCreators.objects.filter(name__in=creators_list))
        context["transfers"] = transfers_list
        context["rights_statements"] = rights_statements
        return context

    def get(self, request, *args, **kwargs):
        """Performs initial grouping of transfer data."""
        if is_ajax(request):
            return self.handle_ajax_request(request)
        return super().get(self, request, *args, **kwargs)

    def grouped_transfer_data(self, transfers_list):
        """Returns grouped data from all transfers in an accession."""
        notes = {"appraisal": []}
        dates = {"start": [], "end": []}
        descriptions_list = []
        languages_list = []
        extent_files = 0
        extent_size = 0
        for transfer in transfers_list:
            bag_data = transfer.bag_data
            extent_size = extent_size + int(bag_data.get("payload_oxum", "0.0").split(".")[0])
            extent_files = extent_files + int(bag_data.get("payload_oxum", "0.0").split(".")[1])
            dates["start"].append(bag_data.get("date_start", ""))
            dates["end"].append(bag_data.get("date_end", ""))
            notes["appraisal"].append(bag_data.get("appraisal_note", ""))
            descriptions_list.append(bag_data.get("internal_sender_description", ""))
            languages_list += [lang for lang in bag_data.get("language", [])]
        languages_list = list(set(languages_list))
        record_type = bag_data.get("record_type", "")
        return notes, dates, descriptions_list, languages_list, extent_files, extent_size, record_type

    def handle_ajax_request(self, request):
        """Handles JavaScript AJAX requests."""
        rdata = {}
        rdata["success"] = False
        if "resource_id" in request.GET:
            try:
                client = ArchivesSpaceClient(
                    settings.ASPACE["baseurl"],
                    settings.ASPACE["username"],
                    settings.ASPACE["password"],
                    settings.ASPACE["repo_id"],
                )
                resp = client.get_resource(request.GET.get("resource_id"))
                rdata["title"] = "{} ({})".format(resp["title"], resp["id_0"])
                rdata["uri"] = resp["uri"]
                rdata["success"] = True
            except Exception as e:
                rdata["error"] = str(e)
        return self.render_to_json_response(rdata)

    def parse_language(self, languages_list):
        """Parses a single language from a list of language codes, and a returns
        a LanguageCode object matching that code.
        """
        if len(languages_list) == 1:
            language = LanguageCode.objects.get_or_create(code=languages_list[0])[0]
        elif len(languages_list) > 1:
            language = LanguageCode.objects.get_or_create(code="mul")[0]
        else:
            language = LanguageCode.objects.get_or_create(code="und")[0]
        return language

    def parse_title(self, organization, record_type, creators_list):
        """Creates a title for the accession."""
        return ("{}, {} {}".format(organization, creators_list, record_type)
                if len(creators_list) > 0 else "{} {}".format(organization, record_type))

    def rights_statement_notes(self, rights_statements):
        """Combines notes from rights statements associated with transfers in an accession."""
        notes = {}
        for statement in rights_statements:
            rights_info = statement.rights_info
            rights_granted = statement.rights_granted.all()
            if not statement.rights_basis.lower() in notes:
                notes[statement.rights_basis.lower()] = []
            notes[statement.rights_basis.lower()].append(
                next(value for key, value in rights_info.__dict__.items()
                     if "_note" in key.lower()))
            for grant in rights_granted:
                notes[statement.rights_basis.lower()].append(
                    grant.rights_granted_note)
        return notes

    def update_accession_rights(self, merged_rights_statements, accession):
        """Associates a list of rights statements with an accession."""
        for statement in merged_rights_statements:
            statement.accession = accession
            statement.save()

    def update_accession_transfers(self, transfers_list, accession):
        """Associates a list of transfers with an accession and updates their status."""
        for transfer in transfers_list:
            BAGLog.log_it("BACC", transfer)
            transfer.process_status = Transfer.ACCESSIONING_STARTED
            transfer.accession = accession
            transfer.save()


class SavedAccessionsDatatableView(ArchivistMixin, BaseDatatableView):
    """Handles processing of requests for Accessions in datatable, making page
    load time more performant."""
    model = Accession
    columns = [
        "title",
        "created",
        "extent_files",
        "accession_transfers__machine_file_identifier",
        "extent_size",
    ]
    order_columns = [
        "title",
        "created",
        "extent_files",
        "accession_transfers__machine_file_identifier",
        "extent_size",
    ]
    max_display_length = 500

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def title(self, accession):
        return (
            "{} ({})".format(accession.title, accession.accession_number)
            if accession.accession_number
            else accession.title
        )

    def transfers(self, accession):
        transfers = accession.accession_transfers.count()
        label = "transfer" if transfers == 1 else "transfers"
        return "{} {}".format(transfers, label)

    def button(self, accession):
        button = "Accession not delivered"
        if self.request.user.can_accession():
            button = (
                '<a href="#" class="btn btn-primary pull-right deliver">Deliver Accession</a>'
                if (accession.process_status < Accession.DELIVERED)
                else '<p class="pull-right" style="margin-right:.7em;">' + accession.get_process_status_display() + "</p>"
            )
        return button

    def prepare_results(self, qs):
        json_data = []
        for accession in qs:
            json_data.append(
                [
                    "<a href='{}'>{}</a.".format(
                        reverse("accession:detail", kwargs={"pk": accession.pk}),
                        self.title(accession),
                    ),
                    accession.created.astimezone(tz.tzlocal()).strftime(
                        "%b %e, %Y %I:%M %p"
                    ),
                    "{} files ({})".format(
                        accession.extent_files, file_size(int(accession.extent_size))
                    ),
                    self.transfers(accession),
                    self.button(accession),
                    accession.pk,
                ]
            )
        return json_data
