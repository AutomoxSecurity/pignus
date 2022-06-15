"""Role Perms Collection
Testing
    Unit Tests: automox/pignus/tests/unit/collections/test_role_perms.py

"""
from pignus.collections.base import Base
from pignus.models.role_perm import RolePerm
from pignus.utils import xlate


class RolePerms(Base):
    def __init__(self, conn=None, cursor=None):
        super(RolePerms, self).__init__(conn, cursor)
        self.table_name = RolePerm().table_name
        self.collect_model = RolePerm

    def get_by_role_id(self, role_id: int) -> list:
        """Get all RolePerms for a given role_id. """
        sql = """
            SELECT *
            FROM `%s`
            WHERE
                `role_id` = %s
        """ % (self.table_name, xlate.sql_safe(role_id))
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        prestines = self.build_from_lists(raws)
        return prestines

# End File: automox/pignus/src/pignus/collections/role_perms.py
