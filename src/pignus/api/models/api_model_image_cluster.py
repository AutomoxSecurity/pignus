"""Api Model Image Cluster
/image-cluster

Testing
    Unit Tests: automox/pignus/tests/unit/api/models/test_api_model_image_cluster.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.image_cluster import ImageCluster


class ApiModelImageCluster(ApiModelBase):

    def __init__(self, event: dict):
        """
        :unit-test: TestApiModelImageCluster().__init__()
        """
        super(ApiModelImageCluster, self).__init__(event)
        self.model = ImageCluster
        self.post_create = True
        self.delete_destroy = True
        self.model_url = "/image-cluster"
        self.perms = {
            "GET": "list-image-clusters",
            "DELETE": "delete-image-clusters"
        }


# End File: automox/pignus/src/pignus/api/models/api_model_image_cluster.py
