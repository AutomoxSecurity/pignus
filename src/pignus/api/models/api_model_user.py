"""Api Model User
/user

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.user import User


class ApiModelUser(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelUser, self).__init__(event)
        self.model = User
        self.post_create = True
        self.delete_destroy = True
        self.modifiable_fields = ["name", "role_id"]
        self.createable_fields = ["name", "role_id"]
        self.model_required_fields = ["name", "role_id"]
        self.model_url = "/user"
        self.perms = {
            "GET": "list-users",
            "POST": "post-users",
            "DELETE": "delete-users",
        }


# End File: automox/pignus/src/pignus/api/api_model_user.py
