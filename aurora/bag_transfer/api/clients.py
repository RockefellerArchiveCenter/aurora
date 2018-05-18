from electronbonder.client import ElectronBond
import json
from os.path import join
from uuid import uuid4

from aurora import settings


class AquariusClient(object):

    def __init__(self):
        self.client = ElectronBond(
            baseurl=settings.AQUARIUS['baseurl'],
            username=settings.AQUARIUS['username'],
            password=settings.AQUARIUS['password'],
        )
        if not self.client.authorize():
            return False
        return True

    def save_accession(self, data):
        resp = self.client.post('transform/', data=data)
        if resp.status_code != 200:
            return False
        return resp.json()
