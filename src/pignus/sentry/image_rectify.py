"""Sentry Image Rectify
Set the appropriate state for an Image record, moving "build_ids" to "last"

"""
from pignus.sentry.image_rectify_sync import ImageRectifySync
from pignus.sentry.image_rectify_scan import ImageRectifyScan
from pignus.utils import date_utils
from pignus.utils import log
from pignus import settings
from pignus.models.image import Image
from pignus.collections.images import Images
from pignus import misc


class ImageRectify:
    def __init__(self):

        self.recitified_sync_images = 0
        self.recitified_sync_containers = 0
        self.recitified_scan_images = 0
        self.recitified_scan_builds = 0
        self.recitified_scan_build_operations = 0
        self.recitified_present_image = 0
        self.recitified_present_container = 0
        self.recitified_maintenence_image = 0
        self.recitified_maintenence_container = 0

        self.cluster_interval = settings.options.get("CLUSTER_PRESENCE_INTERVAL_HOURS", 48)
        self.cluster_supported = settings.options.get("CLUSTER_SUPPORTED", [])

        self.sync_rectify = ImageRectifySync()
        self.scan_rectify = ImageRectifyScan()

    def run(self) -> bool:
        """Handles image rectifies, setting the proper state for all jobs which have completed."""
        images = self.get_images()
        log.info('Checking Rectify on %s images' % len(images), stage="rectify")
        for image in images:
            scan_stats = self.handle_image(image)
            self.recitified_scan_images += scan_stats["recitified_scan_images"]
            self.recitified_scan_builds += scan_stats["recitified_scan_builds"]
            self.recitified_scan_build_operations += \
                scan_stats["recitified_scan_build_operations"]
        log.info("Rectified %s Images" % self.recitified_scan_images, stage="rectify")
        log.info("Rectified %s Containers" % self.recitified_scan_builds, stage="rectify")

        return True

    def get_images(self) -> list:
        """Get Images for the Sentry Rectify process."""
        images = Images().get_for_sentry_rectify()
        return images

    def handle_image(self, image: Image) -> bool:
        """Rectify a single image."""
        if not image.maintained:
            return False

        image.get_builds()
        self.sync_rectify.run(image)
        scan_stats = self.scan_rectify.run(image)
        self.rectify_cluster(image)

        # self.rectify_maintain_status(image)
        return scan_stats

    def rectify_cluster(self, image: Image) -> bool:
        """Check if an image has been seen present in a cluster in the last
        CLUSTER_PRESENCE_INTERVAL_HOURS, by checking the cluster_x_present and cluster_x_last_seen
        fields.
        """
        image.get_builds()
        image.get_clusters()
        image_rectified = False
        for rectify_cluster in self.cluster_supported:
            # If the Image has never been seen in the cluster, continue.
            if rectify_cluster not in image.clusters:
                continue

            # Check each Image Container for it's last time seen.
            for container_digest, container in image.containers.items():
                container.get_clusters()
                if rectify_cluster not in container.clusters:
                    continue

                if not container.clusters[rectify_cluster].present:
                    continue

                expired = date_utils.interval_ready(
                    container.clusters[rectify_cluster].last_seen,
                    self.cluster_interval)
                if not expired:
                    continue

                log.info(
                    "Container hasn't been seen in %s hours in %s cluster, removing." % (
                        self.cluster_interval,
                        rectify_cluster
                    ),
                    image=image,
                    container=container
                )
                image_rectified = True
                container.clusters[rectify_cluster].present = False
                container.clusters[rectify_cluster].save()
                self.recitified_present_container += 1

        if image_rectified:
            self.recitified_present_image += 1

        return True

    def rectify_maintain_status(self, image: Image) -> bool:
        """Check if the image has been seen in any cluster in the last x hours, if not remove it's
        "maintained" status, so that we don't continue to scan and import the image.
        """
        for cluster in self.cluster_supported:
            self._determine_cluster_presence(cluster, image)

            for (
                container_digest,
                container,
            ) in image.builds.items():
                if not container.maintained:
                    continue
                self._determine_cluster_presence(cluster, container)

        # Check if the Image and it's Containers have been seen in any of the supported clusters.
        self._determine_maintain_status(image)

        for container_digest, container in image.containers.items():
            self._determine_maintain_status(container)

    def _determine_cluster_presence(self, cluster: str, entity):
        """Determine if the entity, an Image or Cluster, has been seen in the given cluster in the
        interval hours.
        """
        cluster_fields = misc.get_entity_cluster_fields(cluster)
        cluster_last_seen = getattr(entity, cluster_fields['last_seen'])
        cluster_presence_current = getattr(entity, cluster_fields["present"])
        cluster_presence = True

        # If the image has never been seen in the cluster, set its presence there false.
        if not cluster_last_seen:
            cluster_presence = False

        if cluster_last_seen:
            # If the image has not been seen in the cluster in `interval_hours` set it false
            if misc.interval_ready(cluster_last_seen, self.cluster_interval):
                cluster_presence = False

        # Otherwise the image's cluster presence is True
        if cluster_presence_current != cluster_presence:
            setattr(entity, cluster_fields["present"], cluster_presence)
            entity.save()

    def _determine_maintain_status(self, entity):
        """Determine if the entity, an Image or Cluster, has been seen in any cluters in the last
        maintain interval hours. If it has not, we'll no longer want to sync or scan these
        Images/ Containers. This is achieved by setting it's maintenance to False.
        """
        maintain_interval = 168
        cluster_presence = {}
        for cluster in self.cluster_supported:
            cluster_fields = misc.get_entity_cluster_fields(cluster)
            cluster_last_seen = getattr(entity, cluster_fields['last_seen'])
            # If the image has never been seen in the cluster, set its presence there false.
            if not cluster_last_seen:
                cluster_presence[cluster] = False
                continue

            if cluster_last_seen:
                # If the image has not been seen in the cluster in `interval_hours` set it false
                if misc.interval_ready(cluster_last_seen, maintain_interval):
                    cluster_presence[cluster] = False
                    continue

            cluster_presence[cluster] = True

        maintain = False
        for cluster, presence in cluster_presence.items():
            if presence:
                maintain = True

        if not maintain:
            log.info("%s has not been observed in %s hours, removing maintain status" % (
                entity, maintain_interval))
            entity.maintained = maintain
            entity.save()
        return True

# End File: automox/pignus/src/pignus/sentry/image_rectify.py
