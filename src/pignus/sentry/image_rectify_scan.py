"""Sentry Image Rectify Scan

"""
# import os
# import importlib

from pignus import aws
# from pignus import settings
from pignus.parse.parse_aws import ParseAws
from pignus.parse.parse_trivy import ParseTrivy
from pignus.utils import log
from pignus.collections.scanners import Scanners
from pignus.collections.operations import Operations
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.operation import Operation
from pignus.models.scanner import Scanner
from pignus.models.scan import Scan


class ImageRectifyScan:
    def __init__(self):
        """Set the needed counters to return back out when Rectify is complete."""
        self.recitified_scan_images = 0
        self.recitified_scan_builds = 0
        self.recitified_scan_build_operations = 0

    def run(self, image: Image) -> dict:
        """Check if the image has been scanned recently, if it has extract the details from the scan
        and apply it to the Image and Build.
        """
        self.scanners = Scanners().get_all_enabled()
        rectified = False
        for build_digest, build in image.builds.items():
            rectified_build = self.rectify_scan_build(image, build)
            if rectified_build:
                self.recitified_scan_builds += 1

        if rectified:
            self.recitified_scan_images += 1
            # Set the pending operation flag to none if there are no pending operations.
            build.set_pending_operation()
        ret = {
            "recitified_scan_images": self.recitified_scan_images,
            "recitified_scan_builds": self.recitified_scan_builds,
            "recitified_scan_build_operations": self.recitified_scan_build_operations
        }
        return ret

    def rectify_scan_build(self, image: Image, build: ImageBuild) -> bool:
        """Check if the image has been scanned recently, if it has extract the details from the scan
        and apply it to the Image and ImageBuild.
        """
        if not build.pending_operation == "scan":
            return False

        # Load the Scan Operations that are still pending.
        operations = Operations().get_pending_scans_by_build_id(build.id)

        if not operations:
            log.warning(
                "Could not find operation scan.",
                image=image,
                build=build,
                stage="image-rectify-scan"
            )
            build.set_pending_operation()
            return False

        # Run through all pending Scan Operations for the ImageBuild
        rectified = False
        for operation in operations:
            rectified_operation = self.rectify_scan_build_operation(image, build, operation)
            if rectified_operation:
                rectified = True
                self.recitified_scan_build_operations += 1
        return rectified

    def rectify_scan_build_operation(
            self, image: Image, image_build: ImageBuild, operation: Operation) -> bool:
        """Run the Rectify process for a single Scan Operation."""

        # Load the Build details from AWS
        build_status = self.get_scan_build_status(image, image_build, operation)
        if not build_status:
            return False

        # If the build has completed, clear the build, set the last_build, the build result and
        # build ts
        if not build_status['build_clear']:
            # log.warning(
            #     "Scan build status: %s" % build_status,
            #     image=image,
            #     container=container,
            #     scan="rectify-scan")
            return False

        # Load the Scanner for the CodeBuild scan.
        scanner = self.get_scanner(operation.build_id)
        if not scanner:
            log.error("Could not find scanner for job: %s" % operation.build_id)
            return False

        operation.ended_ts = build_status['build_completed_ts'].datetime
        image_build.scan_last_ts = build_status['build_completed_ts'].datetime

        # Parse the CodeBuild scan, getting CVE data and or potential errors with the scan.
        scan_results = self.parse_scan_log_hack(image, scanner, operation, build_status["build_info"])
        if not scan_results:
            operation.result = False
            operation.save()
            image_build.save()
            return False

        operation.result = build_status["build_result"]
        if scan_results["errors"]:
            log.warning(
                'ImageBuild scan encountered errors: %s' % str(scan_results["errors"]),
                stage="image-rectify-scan-parse",
                image=image,
                image_build=image_build
            )
            operation.result = False
            operation.message = str(scan_results["errors"])
            operation.save()
            image_build.save()
            return True

        # Save the Scan
        scan = Scan()
        scan.get_by_codebuild_id(codebuild_id=build_status["build_info"]["id"])
        scan.ended_ts = build_status["build_completed_ts"]
        scan.cve_critical_nums = scan_results['critical']
        scan.cve_high_nums = scan_results['high']
        scan.cve_medium_nums = scan_results['medium']
        scan.cve_low_nums = scan_results['low']
        scan.cve_unknown_nums = scan_results["unknown"]
        scan.scan_job_success = scan_results["completed_successfully"]
        scan.image_build_id = image_build.id
        scan.save()

        if scan_results["completed_successfully"]:
            scan.scan_job_success = True
            operation.result = True
            operation.message = "Collected CVE data successfully"
        else:
            scan.scan_job_success = False
            operation.result = False
            operation.message = "Scan failed in execution"

        image_build.pending_operation = None
        operation.save()
        image_build.save()
        image.save()
        log.info(
            "Rectified scan",
            image=image,
            image_build=image_build,
            stage="rectify-scan")
        self.recitified_scan_builds += 1
        return True

    def get_scanner(self, build_id: str):
        """Get the Scanner that was used for a CodeBuild scan Operation."""
        codebuild_scan = build_id[build_id.find("-Scan-") + 6: build_id.find(":")]
        the_scanner = None
        for scanner in self.scanners:
            if scanner.name.lower() == codebuild_scan.lower():
                the_scanner = scanner
                return the_scanner

        if not the_scanner:
            log.error("Could not find scanner: %s" % codebuild_scan)
        return False

    def get_scan_build_status(
            self, image: Image, container: ImageBuild, operation: Operation) -> dict:
        """Determine if a give CodeBuild execution has completed, and it's status. If it has, collect
        the CVE detail from the security scans which currently support CVE details.
        """
        ret = {}

        ret["build_info"] = aws.get_build(image, operation.build_id)
        if not ret["build_info"]:
            log.error(
                "Failed to collect details for build: %s" % operation.build_id,
                image=image,
                container=container)
            return False

        if ret["build_info"]["status"] == "FAILED":
            ret["build_clear"] = True
            ret["build_result"] = False
            ret["build_completed_ts"] = ret["build_info"]["end_time"]
        elif ret["build_info"]["status"] == "SUCCEEDED":
            ret["build_clear"] = True
            ret["build_result"] = True
            ret["build_completed_ts"] = ret["build_info"]["end_time"]
        elif ret["build_info"]["status"] == "IN_PROGRESS":
            ret["build_clear"] = False
            return ret
        else:
            log.error(
                'Unknown status for build_id "%s" : %s' % (
                    operation.build_id,
                    ret["build_info"]['status']),
                stage="rectify-scan")
            return False

        return ret

    def parse_scan_log_hack(self, image: Image, scanner: Scanner, operation: Operation, build_info: dict):
        """Parse the scan CodeBuild logs.
        @todo: This needs be done better, by dynamically loading the parser module.
        """
        build_logs = aws.get_build_logs(build_info)
        if not build_logs:
            log.warning("Scan has no logs to parse.", scanner=scanner)
            return False
        if scanner.name == "AWS":
            scan_parse = self.scan_log(image, ParseAws, build_logs)
        elif scanner.name == "Trivy":
            scan_parse = self.scan_log(image, ParseTrivy, build_logs)
        else:
            log.error("Unknown parser: %s" % scanner.name)
            return False

        if build_info["status"] == "FAILED" and scan_parse["errors"]:
            log.warning(
                'Scan failed encountered "%s" for build id: %s' % (
                    scan_parse["errors"], build_info["id"])
            )

        return scan_parse

    def scan_log(self, image, parser, logs: dict):
        return parser().parse(image, logs)


# End File: automox/pignus/src/pignus/sentry/image_rectify_scan.py
