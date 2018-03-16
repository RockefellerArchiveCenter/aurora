# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from orgs.models import Organization,User,BAGLogCodes,BAGLog,Archives,BagInfoMetadata
from orgs.accession.models import Accession


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

@admin.register(LanguageCode)
class BagInfoMetadata(admin.ModelAdmin):
	pass
