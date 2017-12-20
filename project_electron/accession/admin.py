# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from accession.models import *

@admin.register(Accession)
class AccessionAdmin(admin.ModelAdmin):
	pass
