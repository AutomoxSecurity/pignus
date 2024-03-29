"""User Model

"""
from werkzeug.security import generate_password_hash, check_password_hash

from pignus.models.base_entity_meta import BaseEntityMeta
from pignus.models.role import Role
from pignus.collections.api_keys import ApiKeys
from pignus import misc
from pignus.utils import log


FIELD_MAP = [
    {
        "name": "name",
        "type": "str",
    },
    {
        "name": "last_login",
        "type": "datetime",
    },
    {
        "name": "role_id",
        "type": "int",
    },
    {
        "name": "client_id",
        "type": "str",
    },
    {
        "name": "client_secret",
        "type": "str",
    },
]


class User(BaseEntityMeta):

    model_name = "user"

    def __init__(self, conn=None, cursor=None):
        super(User, self).__init__(conn, cursor)
        self.table_name = "users"
        self.metas = {}
        self.field_map = FIELD_MAP
        self.setup()

    def __repr__(self):
        if self.id:
            return "<User %s: %s>" % (self.id, self.name)
        else:
            return "<User>"

    def check_password(self, password):
        check_password_hash("database_record", password)

    def create_random_credentials(self) -> dict:
        """Create a random password. """
        ret = {}
        ret["plaintext_client_id"] = misc.generate_random_digest()[10:30]
        ret["plaintext_client_secret"] = misc.generate_random_digest()[10:40]
        ret["hashed_client_secret"] = generate_password_hash(ret["plaintext_password"], "sha256")
        return ret

    def create_new_user(self, user_email, user_role_slug: str) -> dict:
        """Create a new user with an email, a role slug name."""
        role = Role()
        role.get_by_slug(user_role_slug)
        if not role:
            log.error('Cannot create User, cannot find role: "%s""' % user_role_slug)
            return False

        credentials = self.create_random_credentials()

        self.email = user_email
        self.role_id = role.id
        self.client_id = credentials["plaintext_client_id"]
        self.client_secret = credentials["hashed_client_secret"]
        # self.api_key = aws.

        return {
            "user_id": self.id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "api_key": self.api_key,
        }

    def delete(self) -> bool:
        """Delete a User and its ApiKeys."""
        user_api_keys = ApiKeys().get_api_keys_for_user(self.id)
        for user_key in user_api_keys:
            user_key.delete()

        super(User, self).delete()
        return True


# End File: automox/pignus/src/pignus/models/user.py
