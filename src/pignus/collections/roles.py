"""Roles Collection

Testing
    Unit Tests: automox/pignus/tests/unit/collections/test_roles.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.collections.base import Base
from pignus.models.role import Role


class Roles(Base):
    def __init__(self, conn=None, cursor=None):
        super(Roles, self).__init__(conn, cursor)
        self.table_name = Role().table_name
        self.collect_model = Role


# End File: automox/pignus/src/pignus/collections/roles.py
