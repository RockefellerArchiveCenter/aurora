# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class BagTransferConfig(AppConfig):
    name = 'bag_transfer'

    def ready(self):
        import bag_transfer.signals
