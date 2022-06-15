"""Api Model Image
/image

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.image import Image
from pignus.models.entity_meta import EntityMeta
from pignus import misc
from pignus.utils import log


class ApiModelImage(ApiModelBase):

    def __init__(self, event: dict):
        super(ApiModelImage, self).__init__(event)
        self.model = Image
        self.unique_image_fields = ["id", "auth"]
        self.resource_handled = False
        self.post_create = True
        self.delete_destroy = True
        self.modifiable_fields = ["maintained", "state", "state_msg"]
        self.createable_fields = ["maintained", "name", "repositories"]
        self.model_url = "/image"
        self.perms = {
            "GET": "list-images",
            "POST": "post-images",
            "DELETE": "delete-images"
        }

    def class_routes(self) -> bool:
        """Routes requests to /image to the method which will serve them."""
        path = misc.strip_trailing_slash(self.resource)
        if path == "/image/auth" and self.event["httpMethod"] == "POST":
            self.resource_handled = True
            self.image_auth()
        return True

    def load_model_default(self) -> bool:
        """Default load out for the Image model."""
        self.entity.get_builds()
        self.entity.get_clusters()
        self.entity.load_meta()
        return True

    def class_post_create_validate(self) -> bool:
        """Method for Api Model's to override to add their custom validation for POST requests."""
        if not self.get_arg("name"):
            self.response["status"] = "Error"
            self.response["status_code"] = 401
            self.response["message"] = "Missing required 'name'"
            return False
        if not self.get_arg("repositories"):
            self.response["status"] = "Error"
            self.response["status_code"] = 401
            self.response["message"] = "Missing required 'repositories'"
            return False
        return True

    def post(self):
        """Handle a POST request on a /{image, updating or creating an model via the API.
        :unit-test: TestApiModelBase.test__post
        """
        parent = super(ApiModelImage, self).post()
        return parent

    def image_auth(self):
        """Handle the /image/auth route which is used by Sentry Auth to notify Pignus that an
        Image has been updated in it's parent account with the access IAM policy needed for Pignus
        to sync the Image.
        """
        if not self.perm_check("post-image-auth"):
            self.response_403()
            return False

        # Get the AWS account we're taking auth from
        aws_account = self.get_arg("aws_account")
        if not aws_account:
            self.response_401("AWS account number required.")
            return False
        status = self.get_arg("status")
        if not status:
            self.response_401("Value for: status number required.")
            return False

        # Get the Image
        found = self.find_entity()
        if not found:
            self.response_404()
            return False

        # Check the Images meta to see if it cares about auth.
        ecr_fail_meta_key = "ecr-fail-%s" % aws_account
        if ecr_fail_meta_key not in self.entity.metas:
            self.response_401("Image does not need auth updating")
            return False

        self._update_image_auth()

        self.response["status_code"] = 201
        self.response["data"]["messsage"] = "Image auth modification was a success"
        log.info("Updated %s auth" % self.entity, image=self.entity, state="image-ecr-auth")
        return True

    def _update_image_auth(self):
        """
        """
        aws_account = self.get_arg("aws_account")
        status = self.get_arg("status")
        ecr_fail_meta_key = "ecr-fail-%s" % aws_account

        # Create the ecr-auth status key if it doesnt exist
        stauts_key = "ecr-auth-%s" % aws_account
        if stauts_key not in self.entity.metas:
            self.entity.metas[stauts_key] = EntityMeta()
            self.entity.metas[stauts_key].name = stauts_key
            self.entity.metas[stauts_key].type = "bool"
            self.entity.metas[stauts_key].entity_type = "images"
            self.entity.metas[stauts_key].entity_id = self.entity.id

        # If the auth process was a success
        if status:
            log.debug("Status success, deleting meta key", stage="image-ecr-auth")
            self.entity.metas[ecr_fail_meta_key].delete()
            self.entity.metas[stauts_key].value = True
            self._update_image_build_auth(aws_account)
        else:
            self.entity.metas[stauts_key].value = False

        self.entity.metas[stauts_key].save()

    def _update_image_build_auth(self, aws_account=str) -> bool:
        """If the Image Auth was successfull
        """
        self.entity.get_builds()
        image_builds_flagged_for_sync = 0
        aws_account_ecr = "%s.dkr.ecr.us-west-2.amazonaws.com" % aws_account
        for digest, image_build in self.entity.builds.items():
            if not image_build.maintained:
                continue

            if image_build.repository == aws_account_ecr:
                continue

            image_build.sync_enabled = True
            image_build.sync_flag = True
            image_build.save()
            image_builds_flagged_for_sync += 1

        log_msg = "Updated Image %s to sync %s builds from %s" % (
            self.entity,
            image_builds_flagged_for_sync,
            aws_account)
        log.info(log_msg, image=self.entity, stage="image-ecr-auth")
        return True

# End File: automox/pignus/src/pignus/api/models/api_model_image.py
