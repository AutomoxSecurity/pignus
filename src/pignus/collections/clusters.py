"""Clusters Collection

Testing
    Unit Tests: automox/pignus/tests/unit/collections/test_cluster.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.collections.base_entity_metas import BaseEntityMetas
from pignus.models.cluster import Cluster


class Clusters(BaseEntityMetas):

    collection_name = "clusters"

    def __init__(self, conn=None, cursor=None):
        """Clusters Collection"""
        super(Clusters, self).__init__(conn, cursor)
        self.table_name = "clusters"
        self.collect_model = Cluster

# End File: automox/pignus/src/pignus/collections/clusters.py
