"""Cluster Cve Model

Testing
Unit Tests at automox/pignus/tests/unit/model/test_cluster_cve.py

"""
from pignus.models.base import Base


FIELD_MAP = [
    {
        'name': 'observed_ts',
        'type': 'datetime',
    },
    {
        'name': 'scheduled',
        'type': 'bool',
        'default': 1,
    },
    {
        'name': 'cluster_id',
        'type': 'int',
    },
    {
        'name': 'cve_critical_int',
        'type': 'int'
    },
    {
        'name': 'cve_critical_nums',
        'type': 'list'
    },
    {
        'name': 'cve_critical_images',
        'type': 'list'
    },
    {
        'name': 'cve_high_int',
        'type': 'int'
    },
    {
        'name': 'cve_high_nums',
        'type': 'list'
    },
    {
        'name': 'cve_high_images',
        'type': 'list'
    },
    {
        'name': 'cve_medium_int',
        'type': 'int'
    },
    {
        'name': 'cve_medium_nums',
        'type': 'list'
    },
    {
        'name': 'cve_medium_images',
        'type': 'list'
    },
    {
        'name': 'cve_low_int',
        'type': 'int'
    },
    {
        'name': 'cve_low_nums',
        'type': 'list'
    },
    {
        'name': 'cve_low_images',
        'type': 'list'
    },
]


class ClusterCve(Base):

    model_name = "cluster_cve"

    def __init__(self, conn=None, cursor=None):
        """Create the ClusterCve instance.
        :unit-test: TestClusterCVE::test____init__
        """
        super(ClusterCve, self).__init__(conn, cursor)
        self.table_name = 'cluster_cves'
        self.field_map = FIELD_MAP
        self.setup()

    def __repr__(self):
        """Set the class representation
        :unit-test: TestClusterCVE::__repr__
        """
        if not self.id:
            return "<ClusterCve>"
        else:
            return "<ClusterCve %s>" % (self.id)


# End File: automox/pignus/src/pignus/models/cluster_cve.py
