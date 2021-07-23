from bag_transfer.accession.models import Accession
from bag_transfer.models import (BagInfoMetadata, BagItProfile,
                                 BagItProfileBagInfo, BAGLog, BAGLogCodes,
                                 LanguageCode, Organization, RecordCreators,
                                 Transfer, User)
from bag_transfer.rights.models import (RecordType, RightsStatement,
                                        RightsStatementCopyright,
                                        RightsStatementLicense,
                                        RightsStatementOther,
                                        RightsStatementRightsGranted,
                                        RightsStatementStatute)
from django.contrib import admin


@admin.register(Organization)
class OrganizationsAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(BAGLogCodes)
class BagCodesAdmin(admin.ModelAdmin):
    pass


@admin.register(BAGLog)
class BagLogAdmin(admin.ModelAdmin):
    pass


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    pass


@admin.register(BagInfoMetadata)
class BagInfoMetadata(admin.ModelAdmin):
    pass


@admin.register(Accession)
class AccessionAdmin(admin.ModelAdmin):
    pass


@admin.register(BagItProfile)
class BagItProfile(admin.ModelAdmin):
    pass


@admin.register(BagItProfileBagInfo)
class BagItProfileBagInfo(admin.ModelAdmin):
    pass


@admin.register(LanguageCode)
class LanguageCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatement)
class RightsStatementAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatementCopyright)
class RightsStatementCopyrightAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatementLicense)
class RightsStatementLicenseAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatementStatute)
class RightsStatementStatuteAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatementOther)
class RightsStatementOtherAdmin(admin.ModelAdmin):
    pass


@admin.register(RightsStatementRightsGranted)
class RightsStatementRightsGrantedAdmin(admin.ModelAdmin):
    pass


@admin.register(RecordType)
class RecordType(admin.ModelAdmin):
    pass


@admin.register(RecordCreators)
class RecordCreators(admin.ModelAdmin):
    pass
