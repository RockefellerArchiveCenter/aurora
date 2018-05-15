# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from bag_transfer.models import *
from bag_transfer.accession.models import Accession
from bag_transfer.rights.models import *


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


@admin.register(Archives)
class ArchivesAdmin(admin.ModelAdmin):
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
class BagInfoMetadata(admin.ModelAdmin):
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
