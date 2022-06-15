"""Stats Collection

"""
from datetime import timedelta

import arrow

from pignus import settings
from pignus.utils import xlate
from pignus.utils import date_utils


class Stats:
    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        if not self.conn:
            self.conn = settings.db["conn"]
        self.cursor = cursor
        if not self.cursor:
            self.cursor = settings.db["cursor"]

    def get_number_of_scans(self, since_seconds_ago: int):
        """
        """
        now = date_utils.now()
        since = now().datetime - timedelta(seconds=since_seconds_ago)
        sql = """
            SELECT COUNT(*)
            FROM `scans`
            WHERE
                `created_ts` > "%s"
        """ % xlate.sql_safe(since)
        print(sql)

    def get_clusters_last_seen(self, cluster_names: list) -> dict:
        """Get clusters last seen for a given list of clusters."""
        ret = {}
        for cluster_name in cluster_names:
            args = {
                "cluster_name": cluster_name
            }
            sql = """
                SELECT last_seen
                FROM `image_clusters`
                WHERE
                    `cluster` = %(cluster_name)s
                ORDER BY `last_seen` DESC
                LIMIT 1;"""
            self.cursor.execute(sql, args)
            raw = self.cursor.fetchone()
            if not raw:
                ret[cluster_name] = None
                continue
            ret[cluster_name] = raw[0]

        return ret

    def get_operations_numbers(self, since_hours: int = None) -> dict:
        """Get the number of import/ scan operations ran ever, or in the number of hours passed in.
        """
        since_sql = ""
        if since_hours:
            val_since = arrow.utcnow().shift(hours=since_hours * -1).datetime
            since_sql = 'AND `created_ts` > "%s"' % val_since
        sql = """
            SELECT DISTINCT(`type`), count(*)
            FROM `operations`
            WHERE `entity_type` = "image_builds" %s
            GROUP BY 1;
        """ % since_sql
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        ret = {}
        for raw in raws:
            if raw[0] == "sync":
                ret["sync"] = raw[1]
            elif raw[0] == "scan":
                ret["scan"] = raw[1]

        return ret

    def get_sync_operations(self, hours=24):
        sql = """
            SELECT count(*)
            FROM `operations`
            WHERE
                `type`= "sync" AND
                `created_ts` >= "%s"
        """ % arrow.utcnow().shift(hours=-24).datetime
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        return raw

    # def get_most_dangerous_by_cluster(self, cluster: str):
    #     sql = """
    #         SELECT i.id
    #         FROM `images` as i
    #             JOIN `image_clusters` as ic
    #                 ON i.id = ic.image_id
    #         WHERE
    #             ic.cluster = "dev" AND
    #             ic.present = 1 and
    #             i.cve_critical_int > 0
    #          ORDER BY i.cve_critical_int DESC;
    #      """

# End File: automox/pignus/src/pignus/collections/stats.py
