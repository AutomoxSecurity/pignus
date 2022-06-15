"""Api Collection ImageBuilds
/image-builds

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_image_builds.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.image_builds import ImageBuilds


class ApiCollectionImageBuilds(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionImageBuilds, self).__init__(event)
        self.collection = ImageBuilds()
        self.response["data"]["object_type"] = "image_build"
        self.collection_url = "/image-builds"

# End File: automox/pignus/src/pignus/api/collections/api_collection_image_builds.py
