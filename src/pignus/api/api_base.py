"""Api Base

Testing
    Unit Tests: automox/pignus/tests/unit/api/test_api_base.py
    11/11 Unit-Tested
    100% Test Coverage!

"""
import json

from pignus.utils import xlate
from pignus.utils import log
from pignus.version import __version__
from pignus import misc
from pignus import settings


class ApiBase:

    def __init__(self, event: dict):
        """Instantiate the Api handler.
        :unit-test: test____init__
        """
        self.response = {
            "status": "Success",
            "status_code": 200,
            "message": "Query successful",
            "version": __version__,
            "data": {},
        }
        self.event = event
        self.perms = {}
        self.uri_subject = None
        self.query_params = {}
        self.post_body = {}
        self.page = 1
        self.errors = []
        self.resource_handled = False
        self.parse_success = self.parse_event()

    def parse_event(self) -> bool:
        """Parse an incoming event to AWS Api Gateway.
        :unit-test: test__parse_event
        """
        if misc.try_path(self.event, "path") and misc.try_path(self.event, "resource"):
            self.set_uri_subject(self.event["resource"], self.event["path"])

        # Parse url query params.
        if misc.try_path(self.event, "queryStringParameters"):
            self.query_params = self.event["queryStringParameters"]
            for param_name, param_value in self.query_params.items():
                tmp = param_value
                tmp = xlate.convert_any_to_native(tmp)
                if isinstance(tmp, str):
                    tmp = xlate.url_decode(param_value)
                self.query_params[param_name] = tmp
        if not self._parse_post_body():
            return False
        self._parse_page()

        return True

    def perm_check(self, perm_name: str = None) -> bool:
        """Check permissions on the Api object to see if we should allow the request.
        :unit-test: TestApiBase::test__perm_check
        """
        user_perms = settings.content["user_perms"]

        # If a given perm_name was submitted, check against that
        if perm_name:
            if perm_name not in user_perms:
                return False
            else:
                return True

        http_method = self.event["httpMethod"]
        if http_method not in self.perms:
            return True

        if not user_perms:
            return True

        method_perm = self.perms[http_method]

        if method_perm not in user_perms:
            return False

        return True

    def _parse_post_body(self) -> bool:
        """If it's a POST request get the contents of the request body.
        :unit-test: test___parse_post_body
        """
        if not misc.try_path(self.event, "body"):
            return True

        # If the post body is already a dict, set it.
        if isinstance(self.event["body"], dict):
            self.post_body = self.event["body"]
            return True

        if not isinstance(self.event["body"], dict):
            try:
                self.post_body = xlate.decode_post_data(self.event["body"])
                return True
            except json.decoder.JSONDecodeError:
                self.response["status"] = "Error"
                self.response["status_code"] = 401
                self.response["message"] = "Could not process post data"
                log.error("Cannot parse post body: %s" % self.event["body"])
                return False

    def verify_post_args(self, required_args: list) -> bool:
        """Verify that the incoming request post body has the required args to fulfill the request.
        :unit-test: test__verify_post_args
        """
        verifed = True

        for required_arg in required_args:

            if required_arg not in self.post_body:
                msg = 'Missing required argument: %s' % required_arg
                self.response["message"] = msg
                verifed = False
                break

        if not verifed:
            self.response["status"] = "Error"
            self.response["status_code"] = 401

        return verifed

    def set_uri_subject(self, resource: str, path: str) -> str:
        """Set the subect_uri class var, which contains the variable piece of data sent by the user
        for a request, such as "busybox:latest" from /image/busybox:latest
        :unit-test: test__set_uri_subject
        """
        log.debug("Setting URI Subject")
        remove = resource[resource.find("{"): resource.find("}") + 1]
        invert = resource.replace(remove, "")
        butterfly = path.replace(invert, "")
        self.uri_subject = xlate.url_decode(butterfly)
        log.debug("URI Subject: %s" % self.uri_subject)
        return self.uri_subject

    def response_401(self, message: str = None) -> dict:
        """Set the response message for a 401 Bad request.
        :unit-test: test__response_401
        """
        self.response["status"] = "Error"
        self.response["status_code"] = 401
        if message:
            self.response["message"] = message
        else:
            self.response["message"] = "Bad request."
        return self.response

    def response_403(self, message: str = None) -> dict:
        """Set the response message for a 403 Unauthorized response.
        :unit-test: test__response_403
        """
        self.response["status"] = "Error"
        self.response["status_code"] = 403
        if message:
            self.response["message"] = message
        else:
            self.response["message"] = "Unauthorized request."
        return self.response

    def response_404(self) -> bool:
        """Set the response message for a 404.
        :unit-test: test__response_404
        """
        self.response["status"] = "Error"
        self.response["status_code"] = 404
        self.response["message"] = "Not found."
        return True

    def get_arg(self, arg_name: str, default=None, as_type: str = ""):
        """Get an argument sent to the API either as a query parameter for a in the POST body. To
        get the argument returned as a specific type, use the as_type param.
        :unit-test: TestApiBase.test__get_arg
        """
        ret = None
        if arg_name in self.query_params:
            ret = self.query_params[arg_name]
        elif arg_name in self.post_body:
            ret = self.post_body[arg_name]
        elif default:
            ret = default
        else:
            return None

        if not as_type:
            return ret

        # Transform the arg to the requested type
        if as_type == "bool":
            ret = xlate.convert_str_to_bool(ret)
        return ret

    def _parse_page(self) -> True:
        """Set the page argument in a standard way.
        :unit-test: TestApiBase.test___parse_parse
        """
        page = self.get_arg("page")
        if not page:
            self.page = 1
        else:
            self.page = int(page)
        return True

    # def check_perm(self) -> bool:
    #     """Check the User's permissions for the given resource, and allow or deny access based on
    #     that information.
    #     """
    #     method = settings.content["method"]
    #     resource = settings.content["path"]
    #     user = settings.content["user"]
    #     user_perms = settings.content["user_perms"]

    #     if method not in self.perms:
    #         log.warning("No Rback criteria for %s on %s" % (method, resource))
    #         return True

    #     # If the permission is not in the user_perms, deny access
    #     if self.perms[method] not in user_perms:
    #         log.warning("User %s denied %s on %s. User does not have %s perm." % (
    #             user,
    #             method,
    #             resource,
    #             self.perms[method]))

    #         self.response["status"] = "Error"
    #         self.response["status_code"] = 403
    #         self.response["message"] = "Action now allowed"
    #         return False

    #     return True


# End File: automox/pignus/src/pignus/api/api_base.py
