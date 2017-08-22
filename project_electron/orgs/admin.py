# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from orgs.models import Organization,User

@admin.register(Organization)
class OrganizationsAdmin(admin.ModelAdmin):
	readonly_fields=('machine_name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	pass