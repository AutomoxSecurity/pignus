"""Sentry Image Rectify Sync

"""
from pignus import aws
from pignus import misc
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.operation import Operation
from pignus.models.entity_meta import EntityMeta
from pignus.parse import parse_codebuild
from pignus.utils import xlate
from pignus.utils import log


class ImageRectifySync:
    def __init__(self):
        self.recitified_sync_image = 0
        self.recitified_sync_build = 0

    def run(self, image: Image) -> bool:
        """Check if the image has been synced recently. If it has the image sync needs to be rectified.

        Sync SUCCEEDED
        image.repository_auth_missing - This should be set false
        image.scan_x_flag - Set true so newly synced image will scan

        Sync FAILED

        Sync SUCCEEDED or FAIL
        image.sync_source_build_id - Should be deleted
        image.sync_source_last_build_id - Should be updated to the value that sync_source_build_id
         held

        """
        # Check if there's a build that hasn't been rectified for the given field, if not continue.
        for build_digest, build in image.builds.items():
            sync_build = self.rectify_sync_build(image, build)
            if sync_build:
                image.save()
                self.recitified_sync_image += 1
        return True

    def rectify_sync_build(self, image: Image, image_build: ImageBuild) -> bool:
        """If the build has completed, clear the build, set the last_build, the build result and
        build ts.
        """
        if not image_build.pending_operation == "sync":
            return False

        operation = Operation()
        if not operation.get_by_image_build_and_type(image_build.id, "sync"):
            log.info("Could not find operation sync.", image=image, image_build=image_build)
            return False

        # Load the Build details from AWS
        build_status = self._determine_build_sync_status(image, operation.build_id)
        if not build_status:
            return False

        if misc.try_path(build_status, "build_completed_ts"):
            operation.end_ts = build_status['build_completed_ts'].datetime

        # Build has not finished yet.
        if not build_status['build_clear']:
            return False

        image_build.sync_last_ts = build_status['build_completed_ts'].datetime
        image_build.pending_operation = None

        # If the sync was successful flag the build for security scan
        if build_status["build_result"]:
            report_message = "Success"
            image_build.scan_flag = True
            image_build.digest_local = build_status["digest_local"]
            operation.result = True
        # If the build failed, report as to why.
        else:
            operation.result = False
            report_message = "Failed"

            image.load_meta()
            image_build.load_meta()
            if build_status["fail_reason"]:
                if build_status["fail_reason"] == "ecr-auth":
                    fail_key = "ecr-fail-%s" % xlate.aws_account_docker_url(
                        image_build.repository)
                    log.warning(
                        "Could not sync image, found an ECR auth failure",
                        image=image,
                        image_build=image_build,
                        stage="rectify-sync",
                        build_id=operation.build_id
                    )

                    operation.message = "ECR auth fail"

                    # Set the Image's details
                    if fail_key not in image.metas:
                        image.metas[fail_key] = EntityMeta()
                        image.metas[fail_key].name = fail_key
                        image.metas[fail_key].type = "bool"
                        image.metas[fail_key].value = True
                        image.metas[fail_key].entity_type = "images"
                        image.metas[fail_key].entity_id = image.id
                        image.metas[fail_key].save()

                    image_build.state = "ERROR"
                    image_build.state_msg = "Cannot sync build"
                    image_build.sync_enabled = False
                    image_build.sync_flag = False
                    image_build.scan_enabled = False
                    image_build.scan_flag = False
            else:
                log.warning(
                    "Unknown fail reason for sync, disabling build",
                    image=image,
                    image_build=image_build,
                    stage="rectify_sync")
                operation.result = False
                operation.message = "Unknown reason for failure"
                image_build.sync_enabled = False
                image_build.sync_flag = False
                image_build.scan_enabled = False
                image_build.scan_flag = False
        operation.save()
        image_build.save()
        image.save()
        self.recitified_sync_build += 1
        log.info(
            "Rectified sync: %s" % report_message,
            image=image,
            image_build=image_build,
            stage="rectify-sync")
        return True

    def _determine_build_sync_status(self, image: Image, build_id: str) -> dict:
        """Determine if a give CodeBuild execution has completed, and it's status. If it has, collect
        the CVE detail from the security scans which currently support CVE details.
        :unit-test: test___determine_build_sync_status
        """
        build_clear = False
        build_result = False
        build_completed_ts = None
        fail_reason = None
        digest_local = None

        # Get the build details from AWS
        build_info = aws.get_build(image, build_id)
        if not build_info:
            log.error("Could not get build ID: %s" % build_id)
            return False

        # If the Sync build failed
        if build_info["status"] == "FAILED":
            build_clear = True
            build_result = False
            build_completed_ts = build_info["end_time"]

            # Check the build logs to determine a reason for the failure.
            build_logs = aws.get_build_logs(build_info)
            fail_reason = parse_codebuild.import_failure(build_logs)
            build_info["fail_reason"] = fail_reason
            pass_fail = False

        elif build_info["status"] == "SUCCEEDED":
            build_clear = True
            build_result = True
            build_logs = aws.get_build_logs(build_info)
            build_completed_ts = build_info["end_time"]
            build_logs = aws.get_build_logs(build_info)
            digest_local = parse_codebuild.successful_sync(build_logs)
            pass_fail = True

        elif build_info["status"] == "IN_PROGRESS":
            build_clear = False
            pass_fail = None
        else:
            log.error(
                'Unknown status for build_id "%s" : %s'
                % (build_id, build_info["status"]),
                stage="rectify_sync",
            )
            pass_fail = None

        ret = {
            "build_clear": build_clear,
            "build_result": build_result,
            "build_completed_ts": build_completed_ts,
            "status_bool": pass_fail,
            "status": build_info["status"],
            "fail_reason": fail_reason,
            "digest_local": digest_local
        }
        return ret

# End File: automox/pignus/src/pignus/sentry/image_rectify_sync.py
