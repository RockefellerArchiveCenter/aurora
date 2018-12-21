import json
from requests import Session


class ArchivesSpaceClientError(Exception): pass


class ArchivesSpaceClient():

    def __init__(self, baseurl, username, password, repo_id):
        self.repo_id = repo_id
        self.baseurl = baseurl
        self.session = Session()
        self.session.headers.update({'Accept': 'application/json'})
        try:
            self.authorize(username, password)
        except Exception as e:
            raise ArchivesSpaceClientError("Couldn't authenticate user credentials for ArchivesSpace: {}".format(e))

    def get_resource(self, resource_id, *args, **kwargs):
        resp = self.session.get(
            "/".join([self.baseurl.rstrip("/"), '/repositories/{repo_id}/resources/{resource_id}']).format(
                repo_id=self.repo_id, resource_id=resource_id))
        if resp.status_code == 200:
            return resp.json()
        else:
            raise ArchivesSpaceClientError(resp.json()['error'])

    def authorize(self, username, password):
        resp = self.session.post(
            "/".join([self.baseurl.rstrip("/"), 'users/{username}/login']).format(username=username),
            params={"password": password, "expiring": False}
        )

        if resp.status_code != 200:
            raise ArchivesSpaceClientError((resp.status_code))
        else:
            session_token = json.loads(resp.text)['session']
            self.session.headers['X-ArchivesSpace-Session'] = session_token
            return session_token
