"""Api Collection Roles
/roles

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_roles.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.roles import Roles


class ApiCollectionRoles(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionRoles, self).__init__(event)
        self.collection = Roles()
        self.response["data"]["object_type"] = "role"
        self.collection_url = "/roles"
        self.perms = {
            "GET": "list-roles",
        }

# End File: automox/pignus/src/pignus/api/collections/api_collection_roles.py
