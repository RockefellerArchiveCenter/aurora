from os import remove
from os.path import isfile, join

from aurora import settings


class CleanupRoutine:
    def run(self, identifier):
        filepath = "{}.tar.gz".format(join(settings.DELIVERY_QUEUE_DIR, identifier))
        if isfile(filepath):
            remove(filepath)
            return "Transfer {} removed.".format(identifier)
        return "Transfer {} was not found.".format(identifier)
