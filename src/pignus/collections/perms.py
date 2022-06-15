"""Perms Collection

Testing
    Unit Tests: automox/pignus/tests/unit/collections/test_perms.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.collections.base import Base
from pignus.models.perm import Perm


class Perms(Base):
    def __init__(self, conn=None, cursor=None):
        super(Perms, self).__init__(conn, cursor)
        self.table_name = Perm().table_name
        self.collect_model = Perm


# End File: automox/pignus/src/pignus/collections/perms.py
