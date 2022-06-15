"""Pignus Api
Primary interface for all Pignus Api requests.

"""
import json

# Import Api Routes
from pignus.api.api_check_in import ApiCheckIn
from pignus.api.api_cve import ApiCve
from pignus.api.api_details import ApiDetails

from pignus.api.models.api_model_api_key import ApiModelApiKey
from pignus.api.models.api_model_cluster import ApiModelCluster
from pignus.api.models.api_model_image import ApiModelImage
from pignus.api.models.api_model_image_build import ApiModelImageBuild
from pignus.api.models.api_model_image_cluster import ApiModelImageCluster
from pignus.api.models.api_model_operation import ApiModelOperation
from pignus.api.models.api_model_option import ApiModelOption
from pignus.api.models.api_model_role import ApiModelRole
from pignus.api.models.api_model_role_perm import ApiModelRolePerm
from pignus.api.models.api_model_scan import ApiModelScan
from pignus.api.models.api_model_scanner import ApiModelScanner
from pignus.api.models.api_model_user import ApiModelUser

from pignus.api.collections.api_collection_api_keys import ApiCollectionApiKeys
from pignus.api.collections.api_collection_clusters import ApiCollectionClusters
from pignus.api.collections.api_collection_images import ApiCollectionImages
from pignus.api.collections.api_collection_image_builds import ApiCollectionImageBuilds
from pignus.api.collections.api_collection_image_build_clusters import \
    ApiCollectionImageBuildClusters
from pignus.api.collections.api_collection_image_clusters import ApiCollectionImageClusters
from pignus.api.collections.api_collection_operations import ApiCollectionOperations
from pignus.api.collections.api_collection_options import ApiCollectionOptions
from pignus.api.collections.api_collection_roles import ApiCollectionRoles
from pignus.api.collections.api_collection_perms import ApiCollectionPerms
from pignus.api.collections.api_collection_role_perms import ApiCollectionRolePerms
from pignus.api.collections.api_collection_scans import ApiCollectionScans
from pignus.api.collections.api_collection_scanners import ApiCollectionScanners
from pignus.api.collections.api_collection_users import ApiCollectionUsers

# Import other Pignus modules
from pignus.collections.options import Options
from pignus.models.user import User
from pignus.utils import log
from pignus.utils import date_utils
from pignus.utils.rbac import Rbac
from pignus.utils.auth import Auth
from pignus import misc
from pignus.utils import misc_server
from pignus import settings
from pignus.utils import db
from pignus.version import __version__


class PignusApi:
    def __init__(self, event: dict, context=None):
        """Initiate the PignusApi instance.
        :unit-test: TestPignusApi.test____init__
        """
        self.event = event
        if "verbosity" not in self.event:
            self.event["verbosity"] = None
        settings.request = event
        settings.context = context
        self.api_response = {}
        self.response_body = {
            "status": "Success",
            "status_code": 200,
            "message": "Query successful",
            "version": __version__,
            "data": {},
        }

    def set_db(self) -> bool:
        """Sets the database connection and cursor into the settings global var to be used
        throughout the api request.
        """
        conn, cursor = db.connect_mysql(settings.server["DATABASE"])
        settings.db["conn"] = conn
        settings.db["cursor"] = cursor
        settings.options = Options(conn, cursor).load_options()
        return True

    def set_request(self) -> bool:
        """Collect info about the request and store it in the global settings, so it can be used
        throughout the api request.
        :unit-test: TestPignusApi.test__set_request
        """
        # Check to see if we have headers from the response
        if "headers" not in self.event:
            log.warning("Cannot find 'headers' in event", event=self.event)
            return False

        # Get the user-agent string
        if "user-agent" in self.event["headers"]:
            settings.content["user-agent"] = self.event["headers"]["user-agent"]

        # Get the original IP address from the request
        if "x-forwarded-for" in self.event["headers"]:
            settings.content["x-forwarded-for"] = self.event["headers"]["x-forwarded-for"]

        # Get the api key
        if "x-api-key" in self.event["headers"]:
            settings.content["api-key"] = self.event["headers"]["x-api-key"]
        else:
            settings.content["api-key"] = None

        # Get the query strings
        if "queryStringParameters" in self.event:
            settings.content["query_string_parameters"] = self.event["queryStringParameters"]

        # Get the request method
        if "httpMethod" in self.event:
            settings.content["method"] = self.event["httpMethod"]

        # Get the request path
        if "path" in self.event:
            settings.content["path"] = self.event["path"]
            # Remove trailing slashes
            settings.content["path"] = misc.strip_trailing_slash(settings.content["path"])
            settings.content["path"] = settings.content["path"].replace("//", "/")

        # log.debug("Set Request: Path - %s" % settings.content["path"])

        return True

    def run(self) -> dict:
        """Application router, sending requests to their desired destination."""
        if "action" not in self.event:
            self.event['action'] = ""

        # Handle Api Gateway requests
        self.set_db()
        self.set_request()
        self.route_request()

        status_code = 200
        if "status_code" in self.api_response:
            status_code = self.api_response["status_code"]
            self.api_response.pop("status_code")

        # status = "OK"
        # if "status" in self.api_response:
        #     status = self.api_response["status"]
        #     self.api_response.pop("status")

        body = {}
        if self.api_response:
            body = self.api_response
        body["version"] = __version__

        http_response = {
            "statusCode": status_code,
            "statusDescription": "%s OK" % (status_code),
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(body),
            "isBase64Encoded": False,
        }
        log.info(
            "Served %s %s" % (
                settings.content["user"],
                self.event["path"]),
            user=settings.content["user"]
        )

        return http_response

    def route_request(self) -> bool:
        """Route the request to the api class which will serve the request."""
        if "path" not in self.event:
            msg = 'Malformed event: "%s"' % self.event
            log.error(msg)
            self.api_response["status"] = "Error"
            self.api_response["status_code"] = 500
            self.api_response["message"] = msg
            return False

        path = settings.content["path"]
        base_path = self._get_base_bath(path)

        # Health check endoint. @todo: Redo routing.
        if base_path == "/health":
            log.debug("System is healthy")
            self.api_response["message"] = "System is healthy"
            return True

        # Handle authentication
        if not self.auth_request():
            return False

        log.info("Routing for: %s" % base_path)
        uri_map = {
            "/api-key": ApiModelApiKey,
            "/api-keys": ApiCollectionApiKeys,
            "/check-in": ApiCheckIn,
            "/cluster": ApiModelCluster,
            "/clusters": ApiCollectionClusters,
            "/cve": ApiCve,
            "/details": ApiDetails,
            "/image": ApiModelImage,
            "/image-build": ApiModelImageBuild,
            "/image-build-clusters": ApiCollectionImageBuildClusters,
            "/image-builds": ApiCollectionImageBuilds,
            "/image-cluster": ApiModelImageCluster,
            "/image-clusters": ApiCollectionImageClusters,
            "/images": ApiCollectionImages,
            "/operation": ApiModelOperation,
            "/operations": ApiCollectionOperations,
            "/option": ApiModelOption,
            "/options": ApiCollectionOptions,
            "/perms": ApiCollectionPerms,
            "/role": ApiModelRole,
            "/role-perm": ApiModelRolePerm,
            "/role-perms": ApiCollectionRolePerms,
            "/roles": ApiCollectionRoles,
            "/scan": ApiModelScan,
            "/scanner": ApiModelScanner,
            "/scanners": ApiCollectionScanners,
            "/scans": ApiCollectionScans,
            "/user": ApiModelUser,
            "/users": ApiCollectionUsers
        }

        if base_path in uri_map:
            self.api_response = uri_map[base_path](self.event).handle()

        elif not path:
            self.api_response["status_code"] = 200
            self.api_response["status"] = "Ok"
            self.api_response["message"] = "Welcome"

        else:
            log.warning("Could not find route: %s" % path)
            log.debug("404 Routing. Event: %s" % self.event)
            self.api_response["status_code"] = 404
            self.api_response["status"] = "Error"
            self.api_response["message"] = "Could not find route"

        return True

    def auth_request(self) -> bool:
        """Authenticate the request by an api key supplied in the request header "x-api-key". Then
        remove the key from the request object so it doesnt get misused later.
        :unit-test: TestPignusApi.test__auth_request()
        """
        api_key_plain_text = settings.content["api-key"]
        if not api_key_plain_text:
            self.api_response["status_code"] = 403
            self.api_response["status"] = "Error"
            self.api_response["message"] = "Missing authentication"
            log.warning("Api-key header missing, dropping request")
            return False

        # Get the RSA key pair
        misc_server.set_keys()

        api_key = Auth().auth_api_key(api_key_plain_text)
        if not api_key:
            self.api_response["status_code"] = 403
            self.api_response["status"] = "Error"
            self.api_response["message"] = "Invalid api key."
            log.warning(
                "Request attempted to login with invalid key.",
                event=self.event
            )
            return False

        # We have a valid key, get its User.
        user = User()
        log.debug("Getting user for Auth User ID: %s" % api_key.user_id)
        user_auth = user.get_by_id(api_key.user_id)
        if not user_auth:
            self.api_response["status_code"] = 403
            self.api_response["status"] = "Error"
            self.api_response["message"] = "Cannot find user."
            log.error(
                "Unable to find User ID: %s" % api_key.user_id,
                event=self.event
            )
            return False

        # User has authenticated successfully.
        now = date_utils.now()
        api_key.last_use = now
        api_key.save()
        user.last_login = now
        user.save()
        log.debug("Authenticated User: %s" % user)
        settings.content["user"] = user

        rbac = Rbac()
        perms = rbac.get_role_perms(user.role_id)
        settings.content["user_perms"] = perms
        return True

    def _get_base_bath(self, path: str) -> str:
        """Get the base of the request path so that we can route the request off the begginging
        portion of the URI.
        """
        if path.count("/") > 1:
            return path[:path.rfind("/")]
        else:
            return path

# End File: automox/pignus/src/pignus/api_gateway.py
