"""Api Collection Operations
/operations

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_operations.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.operations import Operations


class ApiCollectionOperations(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionOperations, self).__init__(event)
        self.collection = Operations()
        self.response["data"]["object_type"] = "operation"
        self.collection_url = "/operations"
        self.where_fields = ["entity_id", "entity_type", "type"]
        self.order_by = {
            "field": "updated_ts",
            "op": "DESC"
        }
        self.perms = {
            "GET": "list-operations"
        }

# End File: automox/pignus/src/pignus/api/api_collection_operations.py
