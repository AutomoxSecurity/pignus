"""Api Check In
/check-in
This is the Api route that Pignus within Kubernetes clusters uses to Check-In Images found within
the cluster it monitors.

Testing
    Unit Tests: automox/pignus/tests/unit/api/test_api_check_in.py
    9/10 methods currently unit tested.

"""
from pignus.api.api_base import ApiBase
from pignus.models.image import Image
from pignus.models.cluster import Cluster
from pignus.collections.clusters import Clusters
from pignus.utils import date_utils
from pignus.utils import log
from pignus import image_add
from pignus import misc


class ApiCheckIn(ApiBase):

    def __init__(self, event: dict):
        """Set Api Check-In parameters
        :unit-test: TestApiCheckIn::.test____init__
        """
        super(ApiCheckIn, self).__init__(event)
        self.response["status_code"] = 201
        self.response["message"] = "Check-In successful"
        self.perms = {
            "POST": "check-in"
        }
        self.clusters = []
        self.clusters_enabled = []

    def handle(self) -> dict:
        """Route requests for /check-in
        :unit-test: TestApiCheckIn::test__handle
        """
        if not self.perm_check():
            return self.response_403()

        self.set_clusters()
        if self.event["httpMethod"] == "POST":
            self.post()
        else:
            self.response_404()

        return self.response

    def set_clusters(self) -> bool:
        """Get all Pignus clusters, setting aside the currently enabled ones for check-ins.
        :unit-test: TestApiCheckIn.test__set_clusters
        """
        self.clusters = self._fetch_clusters()
        self.clusters_enabled = []
        for cluster in self.clusters:
            self.clusters_enabled.append(cluster.slug_name)
        return True

    def post(self) -> bool:
        """Handles the POST request /check-in coming from Kubernetes clusters checking in the
        images they're aware of existing in the cluster.
        :unit-test: TestApiCheckIn::test__post
        """
        verified = self._verify_request()
        if not verified:
            return False

        image, image_build = self.get_image_and_build()
        # Set Image details
        image.maintained = True

        cluster = self._get_cluster()
        if self.post_body["repository"] not in image.repositories:
            image.repositories.append(self.post_body["repository"])

        log.debug("Setting Cluster Observed: %s" % image, stage="check-in", image=image)
        image.set_cluster_observed(cluster_id=cluster.id)
        log.debug("Completed Cluster Observed: %s" % image, stage="check-in", image=image)
        # Set Container details
        image_build.maintained = True
        image_build.set_cluster_observed(cluster_id=cluster.id)

        image.save()
        image_build.save()

        # Set Cluster last_check_in
        # @todo: this can be cleaned up
        for cluster in self.clusters:
            if self.post_body["cluster"] == cluster.slug_name:
                check_in_cluster = cluster
                break
        check_in_cluster.last_check_in = date_utils.now()
        check_in_cluster.save()

        log.info(
            "Image Check In %s" % image,
            image=image,
            image_build=image_build,
            stage="check-in",
        )
        self.response["data"]["image"] = image.json()
        return True

    def _verify_request(self) -> bool:
        """Verify that the /check-in request is valid, checking for required fields and a valid
        cluster.
        :unit-test: TestApiCheckIn::test___verify_request
        """
        required_fields = ["name", "tag", "digest", "repository", "cluster"]
        verified_args = self.verify_post_args(required_fields)
        if not verified_args:
            msg = "Client did not submit required field(s): %s" % self.response["message"]
            self.response["message"] = msg
            log.warning(msg)
            return False

        self.post_body["repository"] = misc.strip_trailing_slash(self.post_body["repository"])
        verify_cluster = self._verify_cluster()
        return verify_cluster

    def _verify_cluster(self) -> bool:
        """Verify that the cluster the request is coming from is a valid and supported cluster.
        :unit-test: TestApiCheckIn:test___verify_cluster
        """
        if self.post_body["cluster"] not in self.clusters_enabled:
            msg = 'Cluster "%s" not supported for check-in.' % self.post_body["cluster"]
            log.warning(
                msg,
                stage="check-in",
                cluster=self.post_body["cluster"],
            )
            self.response["message"] = msg
            self.response["status_code"] = 401
            self.response["status"] = "Error"
            return False
        return True

    def _fetch_clusters(self) -> list:
        """Fetcher for all Cluster objects to make testing easier."""
        return Clusters().get_all()

    def _get_cluster(self) -> Cluster:
        """Get the current Check-In Cluster object that is being posted to the api.
        :unit-test: TestApiCheckIn::test___get_cluster
        """
        for cluster in self.clusters:
            if cluster.slug_name == self.post_body["cluster"]:
                return cluster
        return None

    def get_image_and_build(self) -> tuple:
        """Get the Image and Container models, whether or not they previously existed.
        :unit-test: TestApiCheckIn::test__get_image_and_build
        """
        image = Image()
        found = self._get_image(image)
        if not found:
            add_image_response = image_add.add(self.post_body)
            image = add_image_response["image"]
            build = add_image_response["image_build"]
            log.info("Creating new image.", stage="check-in", image=image)

        else:
            build = image.get_build(self.post_body["digest"], self.post_body["repository"])
            if not build:
                build = image_add.image_build_add(image, self.post_body)
                log.info("Image found.", stage="check-in", image=image)

        return image, build

    def _get_image(self, image: Image) -> bool:
        """Separate out the pulling of the Image to make it easier for testing."""
        return image.get_by_name(self.post_body["name"])

# End File: automox/pignus/src/pignus/api/api_check_in.py
