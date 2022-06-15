"""Api Model Cluster
/cluster

Testing
    Unit
        File       automox/pignus/tests/unit/api/models/test_api_model_cluster.py
        Methods    2/2 methods currently unit tested.
    Regression
        File       automox/pignus/tests/regression/api/test_cluster.py


"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.cluster import Cluster


class ApiModelCluster(ApiModelBase):

    def __init__(self, event: dict):
        """
        :unit-test: TestApiModelCluster().__init__()
        """
        super(ApiModelCluster, self).__init__(event)
        self.model = Cluster
        self.post_create = True
        self.delete_destroy = True
        self.modifiable_fields = ["name", "slug_name", "enabled"]
        self.createable_fields = ["name", "slug_name", "enabled"]
        self.model_url = "/cluster"
        self.perms = {
            "GET": "list-clusters",
            "POST": "post-clusters",
            "DELETE": "delete-clusters",
        }


# End File: automox/pignus/src/pignus/api/models/api_model_cluster.py
