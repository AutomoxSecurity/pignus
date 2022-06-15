"""Api Collection Scans
/scans

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_scans.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.scans import Scans


class ApiCollectionScans(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionScans, self).__init__(event)
        self.collection = Scans()
        self.response["data"]["object_type"] = "scan"
        self.collection_url = "/scans"
        self.where_fields = ["image_id", "image_build_id", "operation_id"]
        self.perms = {
            "GET": "list-images",
        }

# End File: automox/pignus/src/pignus/api/collections/api_collection_scans.py
