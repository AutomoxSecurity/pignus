"""Api Model Api Key
/api_key

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.api_key import ApiKey
from pignus.utils.auth import Auth


class ApiModelApiKey(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelApiKey, self).__init__(event)
        self.model = ApiKey
        self.post_create = True
        self.delete_destroy = True
        self.modifiable_fields = ["enabled", "expiration"]
        self.model_required_fields = ["user_id"]
        self.createable_fields = ["user_id", "enabled", "expiration"]
        self.model_url = "/api-key"
        self.perms = {
            "GET": "list-api-keys",
            "POST": "post-api-keys",
            "DELETE": "delete-api-keys"
        }
        self.auth = Auth()

    def get(self) -> bool:
        """Handle a GET request on /api-key, retrieving a generic model the data if it exists. For
        ApiKey models we'll only show the decrypted plaintext version of the key, if the value
        `show-key=true`.
        """
        super(ApiModelApiKey, self).get()
        show_key = self.get_arg("show-key")
        if self.response["status_code"] == 200 and show_key:
            self.response["data"]["object"]["key"] = self.auth.decrypt(self.entity.key)
        return True

    def post(self) -> bool:
        """Handle a POST request on a /api-key, updating or creating an model via the API. For
        ApiKey models we override the POST action so that we can decrypt the key, before returning
        it back to the User.
        """
        super(ApiModelApiKey, self).post()
        if self.response["status_code"] == 201:
            self.response["data"]["object"]["key"] = self.auth.decrypt(self.entity.key)
        return True

    def _post_create(self) -> bool:
        """When we're creating an ApiKey, make sure we generate one before saving.
        """
        super(ApiModelApiKey, self)._post_create()
        plain_text_key = self.auth.generate_api_key()
        encrypted_key = self.auth.encrypt(plain_text_key)
        self.entity.key = encrypted_key
        return True

# End File: automox/pignus/src/pignus/api/api_model_api_key.py
