"""Image Scan

Testing
Unit Tests at automox/pignus/tests/unit/test_image_scan.py

"""
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.operation import Operation
from pignus.models.scan import Scan
from pignus.models.scanner import Scanner
from pignus.collections.images import Images
from pignus.collections.scanners import Scanners
from pignus import aws
from pignus.utils import log
from pignus.utils import date_utils
from pignus.utils import misc_server


class ImageScan:
    def __init__(self):
        """Class constructor, set and get settings vars we'll need throughout the class.
        @unit-test: test____init__
        """
        self.scans_run = 0
        self.scan_limit = misc_server.get_option_value("SCAN_LIMIT")
        self.scan_interval = misc_server.get_option_value("SCAN_INTERVAL_HOURS")

    def run(self) -> dict:
        """Handles image scanning for all images."""
        self.scanners = Scanners().get_all_enabled()
        images = self.get_images()
        log.info(
            "Found %s Images for scan. Scan interval %s hours, limit %s"
            % (
                len(images),
                self.scan_interval,
                self.scan_limit
            ),
            stage="scan"
        )
        # For each image, attempt to run all ready image_build scan tools.
        for image in images:
            if self.scans_run >= self.scan_limit:
                return True
            self.scan_image(image)

        log.info("Initiated %s image_build scans" % self.scans_run, stage="scan")
        return {}

    def get_images(self) -> list:
        """Get Images that could be ready for scanning. """
        images = Images().get_for_sentry_scan()
        # images = Images().get_test_images()
        return images

    def scan_image(self, image: Image) -> bool:
        """Handles scanning against all enabled scanners for a single image."""
        if not image.maintained:
            return False

        image.get_builds()
        for image_build_digest, image_build in image.builds.items():

            image_build.load_meta()

            if self.scans_run >= self.scan_limit:
                return True
            self.scan_image_build(image, image_build)

        return True

    def scan_image_build(self, image: Image, image_build: ImageBuild):
        """Checks to see if a single image_build is ready for a scan."""
        if not self.scan_ready(image_build):
            return False

        for scanner in self.scanners:
            self.execute_scan(scanner, image, image_build)
        return True

    def scan_ready(self, image_build: ImageBuild) -> bool:
        """Determine if an image is ready for security scanning, returning True if so."""
        if image_build.scan_flag:
            return True
        # log.debug(
        #     "Cant find a reason to scan Container: %s" % container,
        #     container=container,
        #     stage="scan")
        return False

    def execute_scan(self, scanner: Scanner, image: Image, image_build: ImageBuild) -> bool:
        """Run a scan via CodeBuild for a given image, setting the build status to the image record.
        """
        build_id = aws.build_runner(scanner.build_name, image, image_build)
        if not build_id:
            log.error(
                "Could not start build %s" % scanner.build_name,
                image=image,
                image_build=image_build)
            return False
        now = date_utils.now()

        # Create and save the Operation
        operation = Operation()
        operation.type = "scan"
        operation.sub_type = scanner.name
        operation.entity_type = "image_builds"
        operation.entity_id = image_build.id
        operation.build_id = build_id
        operation.start_ts = now
        operation.save()

        scan = Scan()
        scan.image_id = image.id
        scan.image_build_id = image_build.id
        scan.scanner_id = scanner.id
        scan.operation_id = operation.id
        scan.codebuild_id = build_id
        scan.save()

        image_build.pending_operation = "scan"
        image_build.scan_flag = False
        image_build.scan_last_ts = now
        image_build.save()
        log.info(
            "Starting ImageBuild scan",
            image=image,
            image_build=image_build,
            stage="scan",
            scan=scanner.name)
        self.scans_run += 1
        return True


# End File: automox/pignus/src/pignus/sentry/image_scan.py
