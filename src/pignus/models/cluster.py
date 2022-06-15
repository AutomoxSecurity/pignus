"""Cluster Model
A Cluster is the representation of a Kubernetes cluster registered to Pignus.

Testing
    Unit
        File:       automox/pignus/tests/unit/modles/test_cluster.py
        Methods:    9/10 methods currently unit tested.

"""
from pignus.models.base_entity_meta import BaseEntityMeta
from pignus.collections.images import Images
from pignus import misc


FIELD_MAP = [
    {
        'name': 'name',
        'type': 'str',
    },
    {
        "name": "slug_name",
        "type": "str",
        "extra": "UNIQUE"
    },
    {
        'name': 'enabled',
        "type": "bool",
        "default": True
    },
    {
        'name': 'version',
        'type': 'str'
    },
    {
        'name': 'last_check_in',
        'type': 'datetime'
    },
]


class Cluster(BaseEntityMeta):

    model_name = "cluster"

    def __init__(self, conn=None, cursor=None):
        """Create the Cluster instance.
        :unit-test: TestCluster::test____init__
        """
        super(Cluster, self).__init__(conn, cursor)
        self.table_name = "clusters"
        self.field_map = FIELD_MAP
        self.metas = {}
        self.images = {}
        self.setup()

    def __repr__(self):
        """Class representation.
        :unit-test: TestCluster::__repr__
        """
        if self.id:
            return "<Cluster %s:%s>" % (self.id, self.name)
        else:
            return "<Cluster %s>" % (self.name)

    def get_images(self) -> bool:
        """Get all Images in a Cluster.
        :unit-test: TestCluster::test__get_images
        """
        cluster_images = Images().get_by_cluster(cluster_id=self.id)
        for image in cluster_images:
            self.images[image.name] = image
        return True

    def save(self) -> bool:
        """Save a Cluster, adding a slug_name from the name if one does not already exist.
        :unit-test: TestCluster::test__save
        """
        if not self.slug_name:
            self.slug_name = misc.make_slug(self.name)
        return super(Cluster, self).save()

    def json(self) -> dict:
        """Create a JSON friendly output of the model, converting types to friendlies. This
        instance extends the Base Model's json method and adds "clusters" to the output.
        :unit-test: TestCluster::test__json
        """
        json_ret = super(Cluster, self).json()
        json_ret["images"] = {}
        for image_name, image in self.images.items():
            json_ret["images"][image_name] = image.json()
        return json_ret


# End File: automox/pignus/src/pignus/models/cluster.py
