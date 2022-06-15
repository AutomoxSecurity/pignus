"""Sentry Image Sync
Download the latest copy of an image from its source into the current AWS account's private ECR.
Process:
    Get all Pignus Images
    For each Image, check it's Builds to see if it requires an sync.

"""
from pignus.utils import log
from pignus import settings
from pignus import aws
from pignus.utils import date_utils
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.operation import Operation
from pignus.collections.images import Images


class ImageSync:
    def __init__(self):
        self.syncs_run = 0

    def run(self) -> bool:
        """Handles downloading Docker images into the local private ECR repository."""
        sync_limit = settings.options.get("SYNC_LIMIT").value
        images = self.get_images()
        log_msg = "Checking sync on %s images, limit %s." % (
            len(images),
            sync_limit,
        )
        log.info(log_msg, stage="sync")
        for image in images:
            if self.syncs_run >= sync_limit:
                break
            self.sync_image(image)

        log.info("Initiated %s image syncs" % self.syncs_run, stage="sync")
        return True

    def get_images(self) -> list:
        """Collect Images that may be ready for a sync, prioritizing Images/Builds that are
        flagged for a sync.
        """
        images_flagged = Images().get_for_sentry_sync_flagged()

        images_regular = Images().get_for_sentry_sync()

        total_images = images_flagged + images_regular

        res = []
        for image in total_images:
            if image not in res:
                res.append(image)

        return res

    def sync_image(self, image: Image) -> bool:
        """Syncing of an image, checking that we have an ECR repository in ECR to sync builds
        to, and then iterate through all maintained images.
        """
        # @todo: do a check here to make sure we have a repository for the image to be pulled in
        aws.create_repository(image)
        image.get_builds()
        sync_limit = settings.options.get("SYNC_LIMIT").value

        # Check all the ImageBuilds
        for build_digest, image_build in image.builds.items():
            if self.syncs_run >= sync_limit:
                break
            self.sync_image_build(image, image_build)
        image.save()
        return True

    def sync_image_build(self, image: Image, image_build: ImageBuild) -> False:
        """Sync the ImageBuild to the local AWS ECR. Check if the image is sourced from one of the
        other AWS accounts ECR.
        """
        if not self.sync_ready(image, image_build):
            return False

        image_build_repo = image_build.repository
        image_build_url = "%s/%s:%s" % (image_build_repo, image.name, image_build.tags[0])

        # Start Container import CodeBuild job
        sync_build_id = aws.build_container_import(image, image_build)
        if not sync_build_id:
            return False

        now = date_utils.now()

        # Create and save the Operation
        operation = Operation()
        operation.type = "sync"
        operation.entity_type = "image_builds"
        operation.entity_id = image_build.id
        operation.build_id = sync_build_id
        operation.start_ts = now
        operation.save()

        image_build.sync_last_ts = now
        self.syncs_run += 1

        log.info(
            "Started sync: %s" % image_build_url,
            image=image,
            container=image_build,
            stage="sync")

        image_build.pending_operation = "sync"
        image_build.sync_flag = False
        image_build.save()
        return True

    def sync_ready(self, image: Image, image_build: ImageBuild) -> bool:
        """Determine if the image/container are ready for a sync operation to be run. This is
        determined by;
            The container not having an ecr-fail meta value
            The container is not from the production account (temporary)
            The container has not been synced in SYNC_INTERVAL hours
        """
        pull_repository = image_build.repository

        # If the ImageBuild is from the local ECR account, dont pull it.
        if settings.server["AWS"]["AWS_LOCAL_ECR"] == pull_repository:
            image_build.sync_flag = False
            image_build.sync_enabled = False
            image_build.scan_flag = True
            image_build.save()
            log.debug("%s is in the local ECR, dont sync it, but set it to scan." % image_build)
            return False

        # Dont sync ImageBuilds from a repository we've been told not to.
        no_pull_repos = settings.options["NO_PULL_REPOSITORIES"].value
        if image_build.repository in no_pull_repos:
            msg = "Image Build is from a repository %s. which Pignus was configured not to pull "
            msg += "from"
            log.warning(
                msg % (image_build.repository),
                image=image,
                image_build=image_build
            )
            image_build.maintained = False
            image_build.save()
            image_build.set_meta_maintained("Wont sync due to being a no pull repository")
            return False

        if no_pull_repos and pull_repository in no_pull_repos:
            # log.debug(
            #     "Skipping sync, container from no pull repo: %s" % container.repository,
            #     image=image,
            #     container=container,
            #     stage="sync",
            # )
            return False

        if image_build.sync_flag:
            # log.debug(
            #     "Sync - Container flagged for sync",
            #     image=image,
            #     container=container,
            #     stage="sync",
            # )
            return True

        # The Container is ready to be synced.
        # log.debug(
        #     "Sync - time to scan container",
        #     image=image,
        #     container=container,
        #     stage="sync",
        # )

        return True


# End File: automox/pignus/src/pignus/sentry/image_sync.py
