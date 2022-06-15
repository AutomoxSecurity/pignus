"""Api Collection Clusters
/clusters

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_clusters.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.clusters import Clusters


class ApiCollectionClusters(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionClusters, self).__init__(event)
        self.collection = Clusters()
        self.order_by = {
            "field": "last_check_in",
            "op": "DESC"
        }
        self.response["data"]["object_type"] = "cluster"
        self.collection_url = "/clusters"
        self.perms = {
            "GET": "list-clusters",
            "POST": "post-clusters",
            "DELETE": "delete-clusters"
        }

# End File: automox/pignus/src/pignus/api/collections/api_collection_clusters.py
