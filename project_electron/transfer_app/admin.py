# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from transfer_app.models import BAGLogCodes, BAGLog

@admin.register(BAGLogCodes)
class BagCodesAdmin(admin.ModelAdmin):
	pass

@admin.register(BAGLog)
class BagLogAdmin(admin.ModelAdmin):
	pass