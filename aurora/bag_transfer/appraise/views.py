from asterism.file_helpers import remove_file_or_dir
from bag_transfer.lib.mailer import Mailer
from bag_transfer.mixins.authmixins import ArchivistMixin
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import BAGLog, Transfer
from dateutil import tz
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView


class AppraiseView(PageTitleMixin, ArchivistMixin, JSONResponseMixin, ListView):
    template_name = "appraise/main.html"
    page_title = "Appraisal Queue"
    model = Transfer

    def handle_note_request(self, request, upload, rdata):
        if request.GET.get("req_type") == "edit":
            rdata["appraisal_note"] = upload.appraisal_note
        elif request.GET.get("req_type") == "submit":
            upload.appraisal_note = request.GET.get("appraisal_note")
        elif request.GET.get("req_type") == "delete":
            upload.appraisal_note = None

    def handle_appraisal_request(self, request, upload):
        appraisal_decision = 0
        appraisal_decision = int(request.GET.get("appraisal_decision"))
        upload.process_status = (
            Transfer.ACCEPTED if appraisal_decision else Transfer.REJECTED
        )
        BAGLog.log_it(("BACPT" if appraisal_decision else "BREJ"), upload)
        if not appraisal_decision:
            remove_file_or_dir(upload.machine_file_path)
            if upload.user_uploaded:
                email = Mailer()
                email.to = [upload.user_uploaded.email]
                email.setup_message("TRANS_REJECT", upload)
                email.send()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads_count"] = len(Transfer.objects.filter(process_status=Transfer.VALIDATED).order_by("created_time"))
        return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            rdata = {}
            rdata["success"] = 0

            if request.user.is_archivist():
                try:
                    upload = Transfer.objects.get(pk=request.GET.get("upload_id"))
                except Transfer.DoesNotExist as e:
                    rdata["emess"] = e
                    return self.render_to_json_response(rdata)

                if request.GET.get("req_form") == "detail":
                    rdata["object"] = upload.id
                    rdata["success"] = 1

                elif (
                    request.GET.get("req_form") == "appraise" and request.user.can_appraise()
                ):
                    if request.GET.get("req_type") == "decision":
                        self.handle_appraisal_request(request, upload)
                    else:
                        self.handle_note_request(request, upload, rdata)
                    upload.save()
                    rdata["success"] = 1

            return self.render_to_json_response(rdata)
        return super().get(self, request, *args, **kwargs)


class AppraiseDataTableView(ArchivistMixin, BaseDatatableView):
    model = Transfer
    columns = [
        "bag_it_name",
        "organization__name",
        "metadata__record_creators__name",
        "metadata__record_type",
        "machine_file_upload_time",
        "bag_it_name",
    ]
    order_columns = [
        "bag_it_name",
        "organization__name",
        "metadata__record_creators__name",
        "metadata__record_type",
        "machine_file_upload_time",
        "bag_it_name",
    ]
    max_display_length = 500

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def appraise_buttons(self, transfer):
        buttons = '<a type="button" class="transfer-detail btn btn-xs btn-warning" data-toggle="modal" data-target="#modal-detail" aria-expanded="false" href="#">Details</a>'
        if self.request.user.can_appraise():
            if transfer.appraisal_note:
                btn_class = "btn-primary"
                note_class = "edit-note"
                aria_label = 'aria-label="Note exists"'
                note_text = "Edit"
            else:
                btn_class = "btn-info"
                note_class = ""
                aria_label = ""
                note_text = "Add"
            buttons = '<a type=button class="btn btn-xs btn-primary appraisal-accept" href="#">Accept</a>\
                       <a type="button" class="btn btn-xs btn-danger appraisal-reject" href="#">Reject</a>\
                       <a type="button" class="appraisal-note btn btn-xs {} {}" data-toggle="modal" data-target="#modal-appraisal-note" href="#" {}>{} Note</a>\
                       <a type="button" class="transfer-detail btn btn-xs btn-warning" data-toggle="modal" data-target="#modal-detail" aria-expanded="false" href="#">Details</a>'.format(
                btn_class, note_class, aria_label, note_text
            )
        return buttons

    def get_initial_queryset(self):
        return Transfer.objects.filter(process_status=Transfer.VALIDATED)

    def prepare_results(self, qs):
        json_data = []
        for transfer in qs:
            creators = ""
            bag_info_data = transfer.bag_data
            if bag_info_data:
                creators = ("<br/>").join(bag_info_data.get("record_creators"))
            json_data.append(
                [
                    transfer.bag_or_failed_name,
                    transfer.organization.name,
                    creators,
                    bag_info_data.get("record_type"),
                    transfer.machine_file_upload_time.astimezone(tz.tzlocal()).strftime(
                        "%b %e, %Y %I:%M %p"
                    ),
                    self.appraise_buttons(transfer),
                    transfer.id,
                ]
            )
        return json_data
