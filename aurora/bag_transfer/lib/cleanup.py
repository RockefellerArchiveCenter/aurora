# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os.path import join, isfile

from aurora import settings


class CleanupError(Exception): pass


class CleanupRoutine:
    def __init__(self, identifier):
        self.identifier = identifier
        self.dir = settings.DELIVERY_QUEUE_DIR

    def run(self):
        try:
            self.filepath = "{}.tar.gz".format(join(self.dir, self.identifier))
            if isfile(self.filepath):
                remove(self.filepath)
                return "Transfer {} removed.".format(self.identifier)
            return "Transfer {} was not found.".format(self.identifier)
        except Exception as e:
            raise CleanupError(e)
