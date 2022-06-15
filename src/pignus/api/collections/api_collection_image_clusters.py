"""Api Collection Image Clusters
/image-clusters

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_image_clusters.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.image_clusters import ImageClusters


class ApiCollectionImageClusters(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionImageClusters, self).__init__(event)
        self.collection = ImageClusters()
        self.response["data"]["object_type"] = "image_cluster"
        self.collection_url = "/image-clusters"

# End File: automox/pignus/src/pignus/api/collections/api_collection_image_clusters.py
