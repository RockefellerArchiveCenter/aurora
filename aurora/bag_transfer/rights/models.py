from datetime import datetime

from django.db import models

from bag_transfer.models import Organization, Archives
from bag_transfer.accession.models import Accession


# Following models schema from
# https://github.com/artefactual/archivematica/blob/stable/1.6.x/src/dashboard/src/main/models.py#L475-L675
class RecordType(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RightsStatement(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    archive = models.ForeignKey(
        Archives, null=True, blank=True, on_delete=models.CASCADE
    )
    accession = models.ForeignKey(
        Accession,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="rights_statements",
    )
    applies_to_type = models.ManyToManyField(RecordType)
    RIGHTS_BASIS_CHOICES = (
        ("Copyright", "Copyright"),
        ("Statute", "Statute"),
        ("License", "License"),
        ("Other", "Other"),
    )
    rights_basis = models.CharField(choices=RIGHTS_BASIS_CHOICES, max_length=64)

    def __str__(self):
        return "{}: {}".format(self.organization, self.rights_basis)

    def get_rights_info_object(self):
        if self.rights_basis == "Copyright":
            data = RightsStatementCopyright.objects.get(rights_statement=self.pk)
        elif self.rights_basis == "License":
            data = RightsStatementLicense.objects.get(rights_statement=self.pk)
        elif self.rights_basis == "Statute":
            data = RightsStatementStatute.objects.get(rights_statement=self.pk)
        else:
            data = RightsStatementOther.objects.get(rights_statement=self.pk)
        return data

    def get_rights_granted_objects(self):
        return RightsStatementRightsGranted.objects.filter(rights_statement=self.pk)

    def get_table_data(self):
        data = {}
        rights_info = self.get_rights_info_object()
        data["notes"] = ", ".join(
            [
                value
                for key, value in list(rights_info.__dict__.items())
                if "_note" in key.lower()
            ]
        )
        return data

    def get_date_keys(self):
        if self.rights_basis == "Other":
            start_date_key = "other_rights_applicable_start_date"
            end_date_key = "other_rights_applicable_end_date"
        else:
            start_date_key = "{}_applicable_start_date".format(
                self.rights_basis.lower()
            )
            end_date_key = "{}_applicable_end_date".format(self.rights_basis.lower())
        return {"start": start_date_key, "end": end_date_key}

    @staticmethod
    def merge_rights(statement_list):
        def merge_dates(merge_list, dates, merge_to):
            start_dates = []
            end_dates = []
            for merge_item in merge_list:
                start_dates.append(getattr(merge_item, dates["start"]))
                end_dates.append(getattr(merge_item, dates["end"]))
            setattr(merge_to, dates["start"], sorted(start_dates)[0])
            setattr(merge_to, dates["end"], sorted(end_dates)[-1])

        statements_by_type = {}
        merged_statements = []
        for statement in statement_list:
            if not statement.rights_basis.lower() in statements_by_type:
                statements_by_type[statement.rights_basis.lower()] = []
            statements_by_type[statement.rights_basis.lower()].append(statement)
        for statement_group in statements_by_type:
            merged_statement = statements_by_type[statement_group][0]
            merged_rights_info = merged_statement.get_rights_info_object()
            if len(statements_by_type[statement_group]) < 2:
                merged_rights_granted = merged_statement.get_rights_granted_objects()
            else:
                merged_rights_granted = []
                rights_info_to_merge = []
                rights_granted_groups = {}

                for statement in statements_by_type[statement_group]:
                    rights_info_to_merge.append(statement.get_rights_info_object())
                    rights_granted_objects = statement.get_rights_granted_objects()
                    for rights_granted in rights_granted_objects:
                        if (
                            not "{}{}".format(
                                rights_granted.act, rights_granted.restriction
                            )
                            in rights_granted_groups
                        ):
                            rights_granted_groups[
                                "{}{}".format(
                                    rights_granted.act, rights_granted.restriction
                                )
                            ] = []
                        rights_granted_groups[
                            "{}{}".format(
                                rights_granted.act, rights_granted.restriction
                            )
                        ].append(rights_granted)

                date_keys = merged_statement.get_date_keys()
                merge_dates(rights_info_to_merge, date_keys, merged_rights_info)

                for granted_group in rights_granted_groups:
                    merged_group = rights_granted_groups[granted_group][0]
                    merge_dates(
                        rights_granted_groups[granted_group],
                        {"start": "start_date", "end": "end_date"},
                        merged_group,
                    )
                    merged_rights_granted.append(merged_group)

            # Save statement
            merged_statement.pk = None
            merged_statement.archive = None
            merged_statement.save()
            merged_statements.append(merged_statement)

            # Save Rights Info
            merged_rights_info.pk = None
            merged_rights_info.rights_statement = merged_statement
            merged_rights_info.save()

            # Save granted
            for granted in merged_rights_granted:
                granted.pk = None
                granted.rights_statement = merged_statement
                granted.save()

        return merged_statements


class RightsStatementCopyright(models.Model):
    rights_statement = models.ForeignKey(RightsStatement, on_delete=models.CASCADE)
    PREMIS_COPYRIGHT_STATUSES = (
        ("copyrighted", "copyrighted"),
        ("public domain", "public domain"),
        ("unknown", "unknown"),
    )
    copyright_status = models.CharField(
        choices=PREMIS_COPYRIGHT_STATUSES, default="unknown", max_length=64
    )
    copyright_jurisdiction = models.CharField(max_length=2, default="us")
    copyright_status_determination_date = models.DateField(
        blank=True, null=True, default=datetime.now
    )
    copyright_applicable_start_date = models.DateField(blank=True, null=True)
    copyright_applicable_end_date = models.DateField(blank=True, null=True)
    copyright_start_date_period = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    copyright_end_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    copyright_end_date_open = models.BooleanField(default=False)
    copyright_note = models.TextField()


class RightsStatementLicense(models.Model):
    rights_statement = models.ForeignKey(RightsStatement, on_delete=models.CASCADE)
    license_terms = models.TextField(blank=True, null=True)
    license_applicable_start_date = models.DateField(blank=True, null=True)
    license_applicable_end_date = models.DateField(blank=True, null=True)
    license_start_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    license_end_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    license_end_date_open = models.BooleanField(default=False)
    license_note = models.TextField()


class RightsStatementRightsGranted(models.Model):
    rights_statement = models.ForeignKey(RightsStatement, on_delete=models.CASCADE)
    ACT_CHOICES = (
        ("publish", "Publish"),
        ("disseminate", "Disseminate"),
        ("replicate", "Replicate"),
        ("migrate", "Migrate"),
        ("modify", "Modify"),
        ("use", "Use"),
        ("delete", "Delete"),
    )
    act = models.CharField(choices=ACT_CHOICES, max_length=64)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    start_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    end_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    end_date_open = models.BooleanField(default=False)
    rights_granted_note = models.TextField(blank=True, null=True)
    RESTRICTION_CHOICES = (
        ("allow", "Allow"),
        ("disallow", "Disallow"),
        ("conditional", "Conditional"),
    )
    restriction = models.CharField(choices=RESTRICTION_CHOICES, max_length=64)

    def __str__(self):
        return "{}: {}".format(self.act, self.restriction)


class RightsStatementStatute(models.Model):
    rights_statement = models.ForeignKey(RightsStatement, on_delete=models.CASCADE)
    statute_jurisdiction = models.CharField(max_length=2, default="us")
    statute_citation = models.TextField()
    statute_determination_date = models.DateField(blank=True, null=True)
    statute_applicable_start_date = models.DateField(blank=True, null=True)
    statute_applicable_end_date = models.DateField(blank=True, null=True)
    statute_start_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    statute_end_date_period = models.PositiveSmallIntegerField(blank=True, null=True)
    statute_end_date_open = models.BooleanField(default=False)
    statute_note = models.TextField()


class RightsStatementOther(models.Model):
    rights_statement = models.ForeignKey(RightsStatement, on_delete=models.CASCADE)
    OTHER_RIGHTS_BASIS_CHOICES = (
        ("Donor", "Donor"),
        ("Policy", "Policy"),
    )
    other_rights_basis = models.CharField(
        choices=OTHER_RIGHTS_BASIS_CHOICES, max_length=64
    )
    other_rights_applicable_start_date = models.DateField(blank=True, null=True)
    other_rights_applicable_end_date = models.DateField(blank=True, null=True)
    other_rights_start_date_period = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    other_rights_end_date_period = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    other_rights_end_date_open = models.BooleanField(default=False)
    other_rights_note = models.TextField()
