"""Image Cron

"""
import os

from pignus.models.cluster_cve import ClusterCve
from pignus.collections.images import Images
from pignus.models.image import Image
from pignus.utils import date_utils
from pignus.utils import log
from pignus import settings


class ImageCron:
    def __init__(self):
        self.cluster_supported = settings.server["CLUSTER"]["SUPPORTED"]
        self.scheduled = os.environ.get("PIGNUS_CRON_RUNNER", False)
        if self.scheduled == "true":
            self.scheduled = True

    def run_cluster_cve(self) -> bool:
        """Handles image rectifies, setting the proper state for all jobs which have completed."""
        log.info("Running Cluster CVE collection")

        for cluster in self.cluster_supported:
            if cluster == "test":
                continue
            self.handle_cluster(cluster)

        return True

    def handle_cluster(self, cluster_name):
        log.info("Working cluster: %s" % cluster_name)
        image_col = Images()
        image_col.per_page = 1000
        data = image_col.get_by_cluster(cluster_name)
        images = data["objects"]

        cluster_cve = ClusterCve()
        cluster_cve.observed_ts = date_utils.now()
        cluster_cve.scheduled = self.scheduled
        cluster_cve.cluster_name = cluster_name

        cluster_cve.cve_critical_images = []
        cluster_cve.cve_critical_nums = []

        cluster_cve.cve_high_images = []
        cluster_cve.cve_high_nums = []

        for image in images:
            if image.cve_critical_nums:
                self.handle_cve_level(cluster_cve, image, "critical")
                self.handle_cve_level(cluster_cve, image, "high")
                self.handle_cve_level(cluster_cve, image, "medium")
                self.handle_cve_level(cluster_cve, image, "low")

        cluster_cve.save()

        print("CLUSTER: %s" % cluster_name)
        print("Critical: %s" % cluster_cve.cve_critical_int)
        print("High: %s" % cluster_cve.cve_high_int)
        print("Medium: %s" % cluster_cve.cve_medium_int)
        print("Low: %s" % cluster_cve.cve_low_int)

    def handle_cve_level(self, cluster_cve: str, image: Image, cve_level: str):
        # If there are no CVEs at this level associated to the image continue
        image_cve_nums = getattr(image, "cve_%s_nums" % cve_level)
        if not image_cve_nums:
            return True

        cluster_cve_nums = getattr(cluster_cve, "cve_%s_nums" % cve_level)
        for image_cve in image_cve_nums:
            if image_cve not in cluster_cve_nums:
                cluster_cve_nums = cluster_cve_nums + [image_cve]

            cluster_cve_image_ids = getattr(cluster_cve, "cve_%s_images" % cve_level)
            if image_cve not in cluster_cve_image_ids:
                cluster_cve_image_ids = cluster_cve_image_ids + [image.id]

        setattr(cluster_cve, "cve_%s_images" % cve_level, cluster_cve_image_ids)
        setattr(cluster_cve, "cve_%s_nums" % cve_level, cluster_cve_nums)
        setattr(cluster_cve, "cve_%s_int" % cve_level, len(cluster_cve_nums))


# End File: automox/pignus/src/pignus/sentry/image_cron.py
