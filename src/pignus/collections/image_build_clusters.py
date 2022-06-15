"""Image Build Clusters collection
Gets collection of Image Build Clusters

"""
from pignus.collections.base import Base
from pignus.models.image_build_cluster import ImageBuildCluster
from pignus.utils import xlate


class ImageBuildClusters(Base):

    def __init__(self, conn=None, cursor=None):
        """Store database conn/connection and model table_name as well as the model obj for the
        collections target model.
        """
        super(ImageBuildClusters, self).__init__()
        self.table_name = ImageBuildCluster().table_name
        self.collect_model = ImageBuildCluster

    def get_by_image_build_id(self, image_build_id: int) -> list:
        """Get all Container Cluster's for a given Container ID."""
        sql_args = {
            "image_build_id": image_build_id
        }
        sql = """
            SELECT *
            FROM `image_build_clusters`
            WHERE
                `image_build_id` = %(image_build_id)s
            ORDER BY `created_ts` DESC;"""
        self.cursor.execute(sql, sql_args)
        raws = self.cursor.fetchall()
        prestines = self.build_from_lists(raws)
        return prestines

    def get_image_build_clusters(self, image_build_id: int):
        sql = """
            SELECT * FROM `image_build_clusters`
            WHERE
                `image_build_id` = %(image_build_id)s;
        """ % {"image_build_id": xlate.sql_safe(image_build_id)}
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        prestines = self.build_from_lists(raws)
        return prestines

# End File: automox/pignus/src/pignus/collections/image_build_clusters.py
