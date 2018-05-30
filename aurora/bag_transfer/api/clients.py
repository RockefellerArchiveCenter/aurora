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
        if 'identifiers' in resp:
            for identifier in resp['identifiers']:
                if identifier['source'] == 'archivesspace':
                    AccessionExternalIdentifier.objects.create(
                        accession=data,
                        identifier=identifier['identifier'],
                        source='archivesspace',
                    )
        return resp.json()


class FornaxClient(object):

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
        resp = self.client.post('sips/', data=data)
        if resp.status_code != 200:
            return False
        return resp.json()


class AltairClient(object):

    def __init__(self):
        self.client = ElectronBond(
            baseurl=settings.ALTAIR['baseurl'],
            username=settings.ALTAIR['username'],
            password=settings.ALTAIR['password'],
        )
        try:
            self.client.authorize()
        except Exception as e:
            print e

    def get_next_accession_number(self):
        resp = self.client.get('next-accession-number')
        if resp.status_code != 200:
            return False
        return resp.json()['display_string']
