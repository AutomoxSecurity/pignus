"""Api Collection Scanners
/scanners

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_scanners.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.scanners import Scanners


class ApiCollectionScanners(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionScanners, self).__init__(event)
        self.collection = Scanners()
        self.response["data"]["object_type"] = "scanner"
        self.collection_url = "/scanners"
        self.perms = {
            "GET": "list-scanners",
            "POST": "post-scanners",
            "DELETE": "delete-scanners"
        }

# End File: automox/pignus/src/pignus/api/collections/api_collection_scanners.py
