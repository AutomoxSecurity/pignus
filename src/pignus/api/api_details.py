"""Api Details
/details/{segment}
Makes information about the Pignus api available.

"""
from datetime import datetime

import arrow

from pignus.collections.clusters import Clusters
from pignus.collections.images import Images
from pignus.collections.image_clusters import ImageClusters
from pignus.collections.image_builds import ImageBuilds
from pignus.collections.image_build_clusters import ImageBuildClusters
from pignus.collections.operations import Operations
from pignus.collections.scanners import Scanners
from pignus.collections.stats import Stats
from pignus.api.api_base import ApiBase
from pignus.utils import date_utils
from pignus.utils import misc_server
from pignus.utils.rbac import Rbac
from pignus import settings


class ApiDetails(ApiBase):
    def __init__(self, event: dict):
        """Instantiate the Api handler."""
        super(ApiDetails, self).__init__(event)
        self.cluster_interval_hours = settings.options.get("CLUSTER_PRESENCE_INTERVAL_HOURS", 48)
        self.clusters_supported = misc_server.get_option_value("CLUSTERS_SUPPORTED", default=[])

    def handle(self) -> dict:
        """Get the current operating details for the Pignus server.
        :unit-test: test__get_details
        """
        self.parse_event()
        if self.uri_subject == "scans":
            self.response["data"]["details"] = self.get_scans()
        else:
            self.response["data"]["details"] = self.get_general()
        return self.response

    def get_general(self) -> dict:
        """Get general details about the Pignus Api."""
        clusters = self._get_clusters()
        scanners = self._get_scanners()
        user_perms = self._get_user_perms()
        ret = {
            "version": settings.server["VERSION"],
            "environment": settings.server["ENVIRONMENT"],
            "aws": {
                "account": settings.server["AWS"]["ACCOUNT"],
                "region": settings.server["AWS"]["REGION"],
                "can_create_ecr": settings.options.get("AWS_CAN_CREATE_ECR", False),
                "can_delete_ecr": settings.options.get("AWS_CAN_DELETE_ECR", False)
            },
            "cluster": {
                "clusters": clusters,
            },
            "sentry": {
                "sync_limit": None,
                "scan_interval_hours": None,
                "scan_limit": None
            },
            "scanners": scanners,
            "user_perms": user_perms
        }
        return ret

    def get_scans(self) -> dict:
        """Handles api/details/scans getting information on Scans that have been excuted through
        Pignus.
        """
        ret = {
            "scans_run": {
                "last_24_hours": None,
                "last_7_days": None
            }
        }
        return ret

    def _get_clusters(self) -> list:
        """Get all Clusters to return to the details request."""
        clusters = Clusters().get_all()
        ret_clusters = []
        for cluster in clusters:
            ret_clusters.append(cluster.json())
        return ret_clusters

    def _get_scanners(self) -> list:
        """Get all Scanners to return to the details request."""
        scanners = Scanners().get_all()
        ret_scanners = []
        for scanner in scanners:
            ret_scanners.append(scanner.json())
        return ret_scanners

    def _get_user_perms(self) -> list:
        """Get a simplified list of all Permission slug names the current user has access to as a
        list.
        @note: this should move moved to settings.content after user is authed in pignus_api
        """
        this_user = settings.content["user"]
        user_perms = Rbac().get_role_perms(this_user.id)
        return user_perms

    def _get_health(self, ret: dict) -> dict:
        """Get the data for the /details/health endpoint, pulling cluster stats data for all
        supported clusters.
        :unit-test: TestApiDetails.test__get_health
        """
        cluster_stats = self._cluster_health_stats()
        ret["cluster"]["clusters"] = {}
        for cluster_name, last_seen in cluster_stats.items():
            ret["cluster"]["clusters"][cluster_name] = {}
            ret["cluster"]["clusters"][cluster_name]["last_seen"] = date_utils.json_date(last_seen)
            ret["cluster"]["clusters"][cluster_name]["last_seen_human"] = date_utils.human_date(last_seen)
            ret["cluster"]["clusters"][cluster_name]["healthy"] = self._cluster_healthy(last_seen)
        ret["operations"] = self._operations_health()
        return True

    def _cluster_health_stats(self):
        """Run the Stats query to get cluster last seen details."""
        clusters = self.clusters_supported
        return Stats().get_clusters_last_seen(clusters)

    def _cluster_healthy(self, last_check_in: datetime) -> bool:
        """Check if a cluster has not been seen in over x hours.
        :unit-test: TestApiDetails.test___cluster_healthy
        """
        if not last_check_in:
            return False
        unhealthy_minutes = 90
        now = date_utils.now()
        delta = now - arrow.get(last_check_in).datetime
        if delta.total_seconds() > (unhealthy_minutes * 60):
            return False
        else:
            return True

    def _operations_health(self) -> dict:
        """Get the number of operations ran in a given period of time.
        :unit-test: TestApiDetails.test___operations_health
        """
        ops_total = Stats().get_operations_numbers()
        ops_last_day = Stats().get_operations_numbers(24)
        ops_last_hour = Stats().get_operations_numbers(1)
        ret = {
            "ever": ops_total,
            "last_day": ops_last_day,
            "last_hour": ops_last_hour
        }
        return ret

    def get_db(self) -> dict:
        """Handler for /details/db route, getting the total counts for different models."""
        ret = {
            "images": {
                "total": Images().get_count_total(),
                "maintained": Images().get_count_maintained(),
                "image_clusters": ImageClusters().get_count_total(),
            },
            "image_builds": {
                "total": ImageBuilds().get_count_total(),
                "maintained": ImageBuilds().get_count_maintained(),
                "container_clusters": ImageBuildClusters().get_count_total(),
            },
            "metas": {
                "total": "tbd"
            },
            "operations": {
                "total": Operations().get_count_total()
            },
        }
        return ret


# End File: automox/pignus/src/pignus/api/api_details.py
