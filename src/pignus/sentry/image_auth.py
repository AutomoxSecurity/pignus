"""Sentry Image Auth
Process to authorize Pignus to download Images from remote AWS Accounts.
This proccess runs inside AWS accounts where Pignus is not running out of. It queries the Pignus Api
to get a list of images which Pignus cannot fetch due to authorization errors. It then updates the
Images ECR AWS IAM to allow the Pignus AWS account to pull those images.

"""
import json

from pignus.models.image import Image
from pignus.client.rest import Rest
from pignus import aws
from pignus.utils import log


class ImageAuth:

    def __init__(self):
        self.images_authed = 0
        self.aws_account = ""
        self.policy_name = ""
        self.api = Rest()

    def run(self) -> bool:
        """Primary entrypoint for ImageAuth.
        """
        images = self.get_images_missing_auth()
        images = images[:1]
        for image in images:
            resolved = self.update_image_ecr_perm(image)
            if resolved:
                self.images_authed += 1
                log.info(
                    "Resolved Image Auth %s" % image,
                    image=image,
                    stage="sentry-image-ecr-auth"
                )
            else:
                log.warning(
                    "Failed to resolve Image Auth %s" % image,
                    image=image,
                    stage="sentry-image-ecr-auth"
                )
        log.info(
            "Updated ECR Auth for %s Images" % self.images_authed,
            stage="sentry-image-ecr-auth")
        return True

    def get_images_missing_auth(self) -> list:
        """Query the Pignus Api on /images/missing-auth?account=some-account, getting the list of
        Images we want to update permissions on.
        """
        payload = {
            "account": self.aws_account
        }
        response = self.api.images_missing_auth_get(payload)
        if not response:
            log.error("%s: Could not fetch images from Pignus" % response)
            exit(1)
        response_json = response.json()
        images = self.api.objects(response_json)
        log.info("Found %s Images missing auth for account %s" % (len(images), self.aws_account))
        return images

    def update_image_ecr_perm(self, image: Image) -> bool:
        """Check if an Image needs it's ECR perms updated, if so append the IAM policy which allows
        the Pignus AWS account to pull ECR images. Then post back to the Pignus Api informing it of
        the status of the operation.
        """
        log.info("Updating ECR perms on %s" % image)
        if self.image_needs_policy_update(image):
            if self.set_image_policy(image):
                success = self.image_update_pignus_api(image, status=True)
            else:
                log.warning("Failed to update Image", image=image, stage="sentry-image-ecr-auth")
                success = self.image_update_pignus_api(image, status=False)
        else:
            success = self.image_update_pignus_api(image, status=True)
        return success

    def image_needs_policy_update(self, image: Image) -> bool:
        """Check an Image's ECR IAM policy if the Image is missing."""
        iam_policy = aws.get_repository_iam_policy(image)

        if isinstance(iam_policy, bool) and not iam_policy:
            log.error("Error")
            return False

        if iam_policy == {}:
            log.debug("Image does not have any policy currently.")
            return True

        if not iam_policy["policyText"]:
            log.info("Image %s has no existing IAM policy." % image)
            return True

        policy_text = json.loads(iam_policy["policyText"])
        for statement in policy_text["Statement"]:
            if statement["Sid"] == self.policy_name:
                log.info("Image %s already has the policy statement %s" % (image, self.policy_name))
                return False
        log.info("Image %s is missing the policy statement %s" % (image, self.policy_name))
        return True

    def set_image_policy(self, image: Image) -> bool:
        policy_success = aws.set_repoisitory_iam_policy(image)
        if not policy_success:
            log.error("Error Updating repository.")
        return policy_success

    def image_update_pignus_api(self, image: Image, status: bool) -> bool:
        """
        """
        response = self.api.image_auth(
            image_id=image.id,
            aws_account=self.aws_account,
            status=status)

        if response.status_code == 201:
            log.info("Successfully updated %s" % image, image=image, stage="sentry-image-ecr-auth")
            return True
        else:
            log.error(
                "Error updating Image on the Pignus Api",
                image=image,
                stage="sentry-image-ecr-auth")
            return False

# End File: automox/pignus/src/pignus/sentry/image_auth.py
