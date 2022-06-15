"""Api Collection Users
/users

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_users.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.users import Users


class ApiCollectionUsers(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionUsers, self).__init__(event)
        self.collection = Users()
        self.collection_url = "/users"
        self.perms = {
            "GET": "list-images"
        }
        self.order_by = {
            "field": "last_login",
            "op": "DESC"
        }
        self.response["data"]["object_type"] = "user"


# End File: automox/pignus/src/pignus/api/collections/api_collection_users.py
