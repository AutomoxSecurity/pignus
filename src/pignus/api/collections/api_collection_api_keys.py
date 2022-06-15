"""Api Collection Api Keys
/api-keys

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_api_keys.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.api_keys import ApiKeys


class ApiCollectionApiKeys(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionApiKeys, self).__init__(event)
        self.collection = ApiKeys()
        self.response["data"]["object_type"] = "api_key"
        self.collection_url = "/api-keys"
        self.perms = {
            "GET": "list-api-keys",
        }
        self.order_by = {
            "field": "last_use",
            "op": "DESC"
        }
        self.where_fields = ["user_id"]

# End File: automox/pignus/src/pignus/api/collections/api_collection_api_keys.py
