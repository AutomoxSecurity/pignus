"""Api Collection Image Build Clusters
/image-build-clusters

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_image_build_clusters.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.image_build_clusters import ImageBuildClusters


class ApiCollectionImageBuildClusters(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionImageBuildClusters, self).__init__(event)
        self.collection = ImageBuildClusters()
        self.response["data"]["object_type"] = "image_build_cluster"
        self.collection_url = "/image-build-clusters"
        self.perms = {
            "GET": "list-images",
        }

# End File: automox/pignus/src/pignus/api/collections/api_collection_image_build_clusters.py
