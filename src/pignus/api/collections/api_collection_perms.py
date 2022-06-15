"""Api Collection Perms
/perms

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_perms.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.perms import Perms


class ApiCollectionPerms(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionPerms, self).__init__(event)
        self.collection = Perms()
        self.response["data"]["object_type"] = "perm"
        self.collection_url = "/perms"
        self.perms = {
            "GET": "list-perms",
            "POST": "post-perms",
            "DELETE": "delete-perms"
        }
        self.per_page_default = 100
        self.per_page_max = 200

# End File: automox/pignus/src/pignus/api/collections/api_collection_perms.py
