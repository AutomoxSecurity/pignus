"""Users Collection.

Testing
    Unit Tests: automox/pignus/tests/unit/collections/test_users.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.collections.base_entity_metas import BaseEntityMetas
from pignus.models.user import User


class Users(BaseEntityMetas):

    collection_name = "users"

    def __init__(self, conn=None, cursor=None):
        super(Users, self).__init__()
        self.table_name = User().table_name
        self.collect_model = User
        self.order_by = {
            "field": "last_login",
            "op": "DESC"
        }

# End File: automox/pignus/src/pignus/collections/users.py
