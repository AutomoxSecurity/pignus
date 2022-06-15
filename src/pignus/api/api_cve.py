"""Api Cve
/cve

Testing
Unit Tests at automox/pignus/tests/unit/api/test_api_cve.py


"""
from pignus.api.api_base import ApiBase
from pignus.collections.scans import Scans
from pignus.collections.images import Images
from pignus.utils import log
from pignus import settings


class ApiCve(ApiBase):

    def __init__(self, event: dict):
        """
        :unit-test: TestApiCve().__init__()
        """
        super(ApiCve, self).__init__(event)
        self.perms = {
            "GET": "list-cves"
        }

    def handle(self) -> dict:
        """Route requests for /cve
        :unit-test: TestApiCve.handle()
        """
        if not self.perm_check():
            return self.response_403()

        if self.uri_subject == "severity":
            self.severity()
        elif self.event["httpMethod"] == "GET":
            self.get()
        else:
            self.response_404()

        return self.response

    def get(self) -> bool:
        """Get a all images which are susceptible to a CVE. """
        log.debug("CVE-GET: %s" % self.uri_subject)
        cve_number = self.get_arg("number")
        if self.uri_subject:
            cve_number = self.uri_subject
        elif cve_number:
            cve_number = cve_number
        else:
            self.response_401()
            return False

        scans = Scans().find_cve("CVE-2021-3121")
        image_ids = []
        for scan in scans:
            image_ids.append(scan.image_id)

        images = Images().get_by_ids(image_ids)
        self.response["data"]["cve_number"] = cve_number
        self.response["data"]["object_type"] = "image"
        self.response["data"]["objects"] = []
        for image in images:
            self.response["data"]["objects"].append(image.json())
        return True

    def severity(self) -> bool:
        """Get Images that are currently maintained that are known to have severities of a given
        severity level.
        """
        scanner_id = settings.options["DEFAULT_SCANNER"].value
        severity = "CRITICAL"
        collect_entities = Images().get_cve_severity(severity=severity, scanner_id=scanner_id)
        self.response["data"]["objects"]["object_type"] = "image"
        self.response["data"]["pages"] = collect_entities["info"]
        self.response["data"]["objects"] = collect_entities["obects"]
        return True


# End File: automox/pignus/src/pignus/api/api_cve.py
