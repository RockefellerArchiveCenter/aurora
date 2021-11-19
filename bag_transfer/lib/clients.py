from asnake.client import ASnakeClient


class ArchivesSpaceClientError(Exception):
    pass


class ArchivesSpaceClient:
    def __init__(self, baseurl, username, password, repo_id):
        self.client = ASnakeClient(
            baseurl=baseurl,
            username=username,
            password=password)
        self.repo_id = repo_id

    def get_resource(self, resource_id):
        """Returns a JSON representation of a resource, or raises an exception if an error occurs."""
        resource = self.client.get("/repositories/{}/resources/{}".format(self.repo_id, resource_id))
        if resource.status_code == 200:
            return resource.json()
        else:
            raise ArchivesSpaceClientError(resource.json()["error"])
