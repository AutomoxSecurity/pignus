"""Api Model Role
/role

Testing
    Unit Tests: automox/pignus/tests/unit/api/modles/api_model_role.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.role import Role


class ApiModelRole(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelRole, self).__init__(event)
        self.model = Role
        self.model_url = "/role"
        self.perms = {
            "GET": "list-roles",
            "POST": "post-roles",
            "DELETE": "delete-roles"
        }

# End File: automox/pignus/src/pignus/api/models/api_model_role.py
