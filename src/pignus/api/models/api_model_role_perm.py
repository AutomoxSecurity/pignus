"""Api Model Role Perm
/role-perm

Testing
    Unit Tests: automox/pignus/tests/unit/api/modles/api_model_role_perm.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.role_perm import RolePerm


class ApiModelRolePerm(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelRolePerm, self).__init__(event)
        self.model = RolePerm
        self.createable_fields = ["role_id", "perm_id", "enabled"]
        self.modifiable_fields = ["enabled"]
        self.model_url = "/role-perm"
        self.perms = {
            "GET": "list-roles-perms",
            "POST": "post-roles-perms",
            "DELETE": "delete-roles-perms"
        }

# End File: automox/pignus/src/pignus/api/models/api_model_role_perm.py
