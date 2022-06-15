"""Parse Trivy Scan Logs

"""
import json

from pignus.parse.parse_cloudwatch_base import ParseCloudWatchBase
from pignus.utils import log
from pignus import misc


class ParseTrivy(ParseCloudWatchBase):

    def __init__(self):
        super(ParseTrivy, self).__init__()
        self.start_line = "Pignus Scan - "
        self.catch_errors = []
        self.parse_json = True

    def decode_json(self, log_line: list) -> bool:
        try:
            build_json = json.loads(log_line)
        except ValueError:
            return False

        if "Results" not in build_json:
            log.warning("No Reuslts")
            return False

        for result in build_json["Results"]:
            secrets = misc.try_path(result, "Secrets")
            if secrets:
                log.warning("Found secrets")
                log.warning(secrets, image=self.image)

            if "Vulnerabilities" not in result:
                log.warning("No vuln data found")
                log.warning(result)
                continue
            for vuln in result["Vulnerabilities"]:
                vuln_sev = vuln["Severity"].lower()
                vuln_id = vuln["VulnerabilityID"]
                self.data[vuln_sev].append(vuln_id)
        log.debug(self.data, image=self.image)
        self.read_complete = True
        return True


# End File: automox/src/pignus/parse/parse_trivy.py
