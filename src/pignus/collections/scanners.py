"""Scanners Collection

"""
from pignus.collections.base_entity_metas import BaseEntityMetas
from pignus.models.scanner import Scanner


class Scanners(BaseEntityMetas):

    collection_name = "scanners"

    def __init__(self, conn=None, cursor=None):
        """Scanners Collection"""
        super(Scanners, self).__init__(conn, cursor)
        self.table_name = "scanners"
        self.collect_model = Scanner

    def get_all_enabled(self) -> list:
        """Get all scanners currently enabled."""
        sql = """
            SELECT *
            FROM `scanners`
            WHERE `enabled` = 1;"""
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        prestines = self.build_from_lists(raws)
        return prestines

# End File: automox/pignus/src/pignus/collections/scanners.py
