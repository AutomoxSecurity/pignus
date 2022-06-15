"""Rest interface for the Pignus Api

Testing
Unit Tests at automox/pignus/tests/unit/client/test_rest.py
8/13 methods currently unit tested.

"""
import requests

from pignus.models.api_key import ApiKey
from pignus.models.cluster import Cluster
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.image_cluster import ImageCluster
from pignus.models.operation import Operation
from pignus.models.option import Option
from pignus.models.role import Role
from pignus.models.role_perm import RolePerm
from pignus.models.perm import Perm
from pignus.models.scan import Scan
from pignus.models.scanner import Scanner
from pignus.models.user import User
from pignus.utils import log
from pignus import settings


class Rest:

    def __init__(self, api_url: str = None, api_key: str = None):
        """
        :unit-test: TestRest.test____init__()
        """
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = settings.client["API_URL"]
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = settings.client["API_KEY"]
        self.die_response_level = None
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": settings.client["API_UA"],
        }

    def __repr__(self):
        """
        :unit-test: TestRest::test____repr__
        """
        return "<PignusClient>"

    def api_key_get(self, api_key_id: int = None, payload: dict = {}) -> requests.Response:
        """Get an ApiKey from the Pignus api by its ID."""
        if api_key_id:
            payload["id"] = api_key_id
        response = self.request("api-key", payload=payload)
        return response

    def api_key_post(
        self,
        payload: dict = {},
        create: bool = False
    ) -> requests.Response:
        """POST on ApiKey."""
        if "user_id" not in payload and create:
            log.error("Post Api-Key requires a User ID to create.")
            return False
        if create:
            payload["create"] = True
        response = self.request("api-key", payload, "POST")
        return response

    def api_key_delete(self, api_key_id: int = None, payload: dict = {}) -> requests.Response:
        """Get an ApiKey from the Pignus api by its ID."""
        if api_key_id:
            payload["id"] = api_key_id
        response = self.request("api-key", payload=payload, method="DELETE")
        return response

    def api_keys_get(self, payload: dict = {}) -> requests.Response:
        """Get ApiKeys from the Pignus api."""
        response = self.request("api-keys", payload)
        return response

    def check_in_post(self, image_data: dict, cluster: str) -> requests.Response:
        """Check in a single or multiple images to the Pignus Api.
        :unit-test: TestRest:test__check_in_post
        """
        payload = {
            "repository": image_data["repository"],
            "name": image_data["name"],
            "tag": image_data["tag"],
            "digest": image_data["digest"],
            "cluster": cluster,
        }
        for key, value in payload.items():
            if not value:
                log.error("[ERROR] Missing required value for %s" % key)
                log.error("\tCurrent payload %s" % image_data)
                return False
        response = self.request("check-in", payload, method="POST")

        return response

    def cluster_get(
        self,
        cluster_id: int = None,
        cluster_name: str = None,
        cluster_slug_name: str = None,
    ) -> dict:
        """GET Cluster from the Api.
        :unit-test: TestRest::test__cluster_get
        """
        if not cluster_id and not cluster_name and not cluster_slug_name:
            log.error("GET Cluster requires a Cluster ID, Cluster name, or Cluster slug name.")
            return False
        payload = {}
        if cluster_id:
            payload["id"] = cluster_id
        if cluster_name:
            payload["name"] = cluster_name
        if cluster_slug_name:
            payload["slug_name"] = cluster_slug_name
        response = self.request("cluster", payload, "GET")
        return response

    def cluster_post(
        self,
        cluster_id: int = None,
        cluster_name: str = None,
        payload: dict = {},
        create: bool = False
    ) -> dict:
        """POST Cluster updates to the Api.
        :unit-test: TestRest::test__cluster_post
        """
        if not create and not cluster_id:
            log.error("Post Cluster requires a Cluster ID or create flag.")
            return False
        if cluster_id:
            payload["id"] = cluster_id
        if cluster_name:
            payload["name"] = cluster_name
        if create:
            payload["create"] = True
        response = self.request("cluster", payload, "POST")
        return response

    def cluster_delete(self, cluster_id: int = None) -> dict:
        """DELETE a Cluster
        :unit-test: TestRest::test__cluster_delete
        """
        if not cluster_id:
            log.error("Delete Cluster requires a Cluster ID.")
            return False
        payload = {
            "id": cluster_id
        }
        response = self.request("cluster", payload, "DELETE")
        return response

    def clusters_get(self) -> requests.Response:
        """GET all Pignus Clusters.
        :unit-test: TestRest::test__clusters_get
        """
        response = self.request("clusters")
        return response

    def cve_get(self, cve_number: str = "", payload: dict = {}) -> requests.Response:
        """Get CVE data from the Pignus api."""
        if cve_number:
            payload["number"] = cve_number
        response = self.request("cve", payload)
        return response

    def details_get(self, segment: str = None) -> requests.Response:
        """Get details about the Pignus Api.
        :unit-test: TestRest.test__details_get
        """
        if segment:
            response = self.request("details/%s" % segment)
        else:
            response = self.request("details/")

        return response

    def image_get(
        self,
        image_str: str = None,
        image_id: str = None,
        payload: dict = {}
    ) -> requests.Response:
        """Get an Image from Pignus by am image str, or by an Image's ID
        """
        if image_str:
            payload = {
                "name": image_str,
            }
        elif image_id:
            payload = {
                "id": image_id
            }
        response = self.request('image', payload)
        return response

    def image_post(
        self,
        image_id: int = None,
        payload: dict = {},
        create: bool = False
    ) -> requests.Response:
        """POST image updates to the Api.
        """
        if not image_id and not create:
            log.error("Post Image requires an Image ID unless creating.")
            return False
        if image_id:
            payload["id"] = image_id
        if create:
            payload["create"] = True
        response = self.request("image", payload, "POST")
        return response

    def image_delete(self, image_id: str, delete_ecr: bool = False) -> requests.Response:
        """DELETE on /image
        """
        payload = {}
        payload["id"] = image_id
        if delete_ecr:
            payload["delete_ecr"] = delete_ecr
        response = self.request("image", payload, "DELETE")
        return response

    def image_auth(self, image_id: int, aws_account: str, status: bool) -> requests.Response:
        """POST on /image/auth
        Method for Sentry Auth to use when an Image has had it's IAM access policy successfully
        updated. This will tell the Pignus Api that it is now able to pull the Image which lives in
        a different AWS account.
        """
        payload = {
            "id": image_id,
            "aws_account": aws_account,
            "status": status
        }
        response = self.request("image/auth", payload=payload, method="POST")
        return response

    def images_get(self, payload: dict = {}) -> dict:
        """Get Images on the Pignus Api, against /images
        :unit-test: TestRest:test__images_get
        """
        response = self.request("images", payload)
        return response

    def images_search_get(self, payload: dict = {}) -> dict:
        """Get Images search on the Pignus Api."""
        response = self.request("images/search", payload)
        return response

    def images_missing_auth_get(self, payload: dict = {}) -> dict:
        """Get Images missing auth on the Pignus Api. This method requires an account number in the
        payload which maps to an AWS account.
        :unit-test: TestRest:test__images_missing_auth_get
        """
        response = self.request("images/missing-auth", payload)
        return response

    def image_build_get(
        self,
        digest: str = None,
        image_build_id: str = None,
        payload: dict = {}
    ) -> requests.Response:
        """Get an ImageBuild from Pignus by a digest str, or by an ImageBuilds's ID
        """
        if digest:
            payload["digest"] = digest
        elif image_build_id:
            payload["id"] = image_build_id
        response = self.request('image-build', payload=payload)
        return response

    def image_build_post(
        self,
        image_build_id: int = None,
        payload: dict = {},
    ) -> requests.Response:
        """POST updates to the image-build Api.
        :unit-test: TestRest::test__image_build_post
        """
        if image_build_id:
            payload["id"] = image_build_id
        response = self.request("image-build", payload, "POST")
        return response

    def image_build_delete(
        self,
        image_build_id: int = None,
        payload: dict = {},
    ) -> requests.Response:
        """Delete an ImageBuild on the image-build Api.
        :unit-test: TestRest::test__image_build_post
        """
        if image_build_id:
            payload["id"] = image_build_id
        response = self.request("image-build", payload, "DELETE")
        return response

    def image_builds_get(self, payload: dict = {}) -> requests.Response:
        """Get ImageBulds on the Pignus Api.
        :unit-test: TestRest::test__image_builds_get
        """
        response = self.request("image-builds", payload)
        return response

    def image_clusters_get(self, payload: dict = {}) -> dict:
        """Get all ImageClusters on the Pignus Api.
        :unit-test: TestRest::test__image_clusters_get
        """
        response = self.request("image-clusters", payload)
        return response

    def operation_get(self, payload: dict = {}) -> dict:
        """Get a Operation on the Pignus Api.
        :unit-test: TestRest::test__operation_get
        """
        response = self.request("operation", payload)
        return response

    def operations_get(self, payload: dict = {}) -> dict:
        """Get all Operations on the Pignus Api.
        :unit-test: TestRest::test__operations_get
        """
        response = self.request("operations", payload)
        return response

    def option_get(self, option_str: str = None, option_id: str = None) -> requests.Response:
        """Get an Option from Pignus by am image str, or by an Image's ID
        """
        payload = {}
        if option_str:
            payload = {
                "name": option_str,
            }
        else:
            payload = {
                "id": option_id
            }
        response = self.request('option', payload)
        return response

    def option_post(self, option_id: int = None, payload: dict = {}) -> requests.Response:
        """POST Option updates to the Api.
        """
        if not option_id:
            log.error("Post Option requires an Option ID.")
            return False
        if option_id:
            payload["id"] = option_id
        response = self.request("option", payload, "POST")
        return response

    def options_get(self) -> requests.Response:
        """Get an all Options from Pignus.
        :unit-test: TestRest:test__options_get
        """
        response = self.request('options')
        return response

    def perms_get(self, payload: dict = {}) -> dict:
        """Get all Perms on the Pignus Api.
        :unit-test: TestRest:test__perms_get
        """
        response = self.request("perms", payload)
        return response

    def roles_get(self, payload: dict = {}) -> dict:
        """Get all Roles on the Pignus Api.
        :unit-test: TestRest:test__roles_get
        """
        response = self.request("roles", payload)
        return response

    def role_perms_get(self, payload: dict = {}) -> dict:
        """Get all RolePerms on the Pignus Api.
        :unit-test: TestRest:test__role_perms_get
        """
        response = self.request("role-perms", payload)
        return response

    def scan_get(self, payload: dict = {}) -> dict:
        """Get a Scan on the Pignus Api."""
        response = self.request("scan", payload)
        return response

    def scans_get(self, payload: dict = {}) -> dict:
        """Get all Scans on the Pignus Api.
        :unit-test: TestRest:test__scans_get
        """
        response = self.request("scans", payload)
        return response

    def scanner_get(self, scanner_id: int = None, payload: dict = {}) -> requests.Response:
        """Get a Scanner on the Pignus Api.
        :unit-test: TestRest:test__scanner_get
        """
        if scanner_id:
            payload["id"] = scanner_id
        response = self.request("scanner", payload)
        return response

    def scanner_post(self, scanner_id: int = None, payload: dict = {}) -> requests.Response:
        """Get a Scanner on the Pignus Api.
        :unit-test: TestRest:test__scanner_get
        """
        if scanner_id:
            payload["id"] = scanner_id
        response = self.request("scanner", payload, method="POST")
        return response

    def scanners_get(self, page: int = 1) -> dict:
        """Get all Scanners on the Pignus Api.
        :unit-test: TestRest:test__scanners_get
        """
        response = self.request("scanners")
        return response

    def user_get(self, user_id: int = None, payload: dict = {}) -> dict:
        """Get all Users on the Pignus Api.
        :unit-test: TestRest:test__user_get
        """
        payload = payload
        if user_id:
            payload["id"] = user_id
        response = self.request("user", payload)
        return response

    def user_post(
        self,
        user_id: int = None,
        payload: dict = {},
        create: bool = False
    ) -> requests.Response:
        """POST on User."""
        if not user_id and "user_id" not in payload and not create:
            log.error("Post User requires a User str or User ID.")
            return False
        if user_id:
            payload["id"] = user_id
        if create:
            payload["create"] = True
        response = self.request("user", payload, "POST")
        return response

    def user_delete(self, user_id: str) -> requests.Response:
        """DELETE a User.
        """
        payload = {}
        payload["id"] = user_id
        response = self.request("user", payload, "DELETE")
        return response

    def users_get(self, page: int = 1) -> dict:
        """Get all Users on the Pignus Api."""
        response = self.request("users")
        return response

    def get_images_cluster(self, cluster: str) -> requests.Response:
        """Get all images that are currently deployed to a given cluster."""
        return self.request("images/cluster/%s" % cluster)

    def objects(self, response_json: dict, object_type: str = None, direct_xlate=False) -> list:
        """Extract known models into native model objects from a json response."""
        if object_type:
            model_type = object_type
        else:
            model_type = response_json["data"]["object_type"]

        if model_type == "api_key":
            model_object = ApiKey
        elif model_type == "cluster":
            model_object = Cluster
        elif model_type == "image":
            model_object = Image
        elif model_type == "image_build":
            model_object = ImageBuild
        elif model_type == "image_cluster":
            model_object = ImageCluster
        elif model_type == "operation":
            model_object = Operation
        elif model_type == "option":
            model_object = Option
        elif model_type == "role":
            model_object = Role
        elif model_type == "role_perm":
            model_object = RolePerm
        elif model_type == "perm":
            model_object = Perm
        elif model_type == "user":
            model_object = User
        elif model_type == "scan":
            model_object = Scan
        elif model_type == "scanner":
            model_object = Scanner

        else:
            log.error("Unsupported object_type: %s" % model_object)
            return False

        # If we're extracting from a collection of models.
        if isinstance(response_json, dict) and "objects" in response_json["data"]:
            objects = []
            for raw_object in response_json["data"]["objects"]:
                _object = model_object()

                _object.build_from_dict(raw_object)

                objects.append(_object)
            return objects

        # if we're extracting a single model.
        elif isinstance(response_json, dict) and "object" in response_json["data"]:
            _object = model_object()
            # @todo: add scan to the image_build model, this can possibly be removed then
            _object.build_from_dict(response_json["data"]["object"])
            return _object

        elif direct_xlate:
            objects = []
            for data in response_json:
                _object = model_object()
                _object.build_from_dict(data, pass_unexpected=True)
                objects.append(_object)
            return objects

        else:
            log.error("Can not parse response.")
            return False

    def object(self, response_json: dict):
        if response_json["data"]["object_type"] == "api_key":
            model_object = ApiKey
        elif response_json["data"]["object_type"] == "cluster":
            model_object = Cluster
        elif response_json["data"]["object_type"] == "image":
            model_object = Image
        elif response_json["data"]["object_type"] == "user":
            model_object = User
        elif response_json["data"]["object_type"] == "scanner":
            model_object = Scanner
        elif response_json["data"]["object_type"] == "option":
            model_object = Option
        else:
            log.error("Unsupported object_type: %s" % response_json["data"]["object_type"])
            return False

        # We're extracting a single model.
        if isinstance(response_json, dict) and "object" in response_json["data"]:
            _object = model_object()
            _object.build_from_dict(response_json["data"]["object"])
            return _object

        else:
            log.error("Can not parse response.")
            return False

    def request(
        self, url: str, payload: dict = {}, method: str = "GET"
    ) -> requests.Response:
        """Make a request on the Pignus Api.
        :unit-test: TestRest:test__request
        """
        request_args = {
            "headers": self.headers,
            "method": method,
            "url": "%s/%s" % (self.api_url, url),
        }
        if payload:
            if request_args["method"] in ["GET", "DELETE"]:
                request_args["params"] = payload
            elif request_args["method"] == "POST":
                for key, value in payload.items():
                    if isinstance(value, bool):
                        payload[key] = str(value).lower()
                request_args["json"] = payload

        response = requests.request(**request_args)
        if response.status_code >= 500:
            log.error("Pignus Api Error")

        if self.die_response_level:
            if response.status_code >= self.die_response_level:
                print("-- Request Failed --")
                print("Url\t%s" % request_args["url"])
                print("Status\t%s" % response.status_code)
                print("Method\t%s" % request_args["method"])
                # if payload:
                #     print("Params\t%s" % payload)
                print("Response")
                print(response.text)

        return response


# End File: automox/pignus/src/pignus/client/rest.py
