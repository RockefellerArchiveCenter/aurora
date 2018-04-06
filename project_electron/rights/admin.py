# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from rights.models import *

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
