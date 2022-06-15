"""Api Collection Role Perms
/role-perms

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_role_perms.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.role_perms import RolePerms


class ApiCollectionRolePerms(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionRolePerms, self).__init__(event)
        self.collection = RolePerms()
        self.response["data"]["object_type"] = "role_perm"
        self.collection_url = "/role-perms"
        self.perms = {
            "GET": "list-role-perms",
            "POST": "post-role-perms",
            "DELETE": "delete-role-perms"
        }
        self.where_fields = ["role_id", "perm_id"]
        self.per_page_default = 100
        self.per_page_max = 200

# End File: automox/pignus/src/pignus/api/collections/api_collection_role_perms.py
