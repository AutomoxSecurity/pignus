"""Model Container Rest

"""

from pignus.models.rest_base import RestBase
from pignus.models.container import FIELD_MAP


class RestContainer(RestBase):

    def __init__(self, container: dict = None):
        super(RestContainer, self).__init__()
        self.raw = container
        self.clusters = {}
        self.build(FIELD_MAP, container)

    def __repr__(self):
        return "<Container %s>" % self.display()

    def build(self, FIELD_MAP: dict, container: dict) -> bool:
        """Extend the base build so we can hydrate the containers. """
        clusters = {}
        if "clusters" in container:
            clusters = container["clusters"]
            del container["clusters"]
        super(RestContainer, self).build(FIELD_MAP, container)
        for cluster_name, cluster_info in clusters.items():
            self.clusters[cluster_name] = cluster_info
        return True

    def display(self) -> str:
        """Get a pretty display of the Container, if we have a tag use that, if not use the
           digest.
        """
        ret = ""
        if self.tag:
            ret = self.tag
        elif self.digest:
            ret = "@sha256:%s" % self.digest
        return ret

# End File: automox/src/pignus/models/rest_container.py
