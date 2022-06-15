"""Parse AWS ECR Scan Logs

"""
import json

from pignus.parse.parse_cloudwatch_base import ParseCloudWatchBase
from pignus.utils import log
from pignus import misc


class ParseAws(ParseCloudWatchBase):

    def __init__(self):
        super(ParseAws, self).__init__()
        self.start_line = "Pignus Scan - "
        self.catch_errors = [
            "ImageNotFoundException",
            "SCAN_ELIGIBILITY_EXPIRED"
        ]
        self.parse_json = True

    def decode_json(self, log_line):
        try:
            build_json = json.loads(log_line)
        except ValueError:
            return False

        if not misc.try_path(build_json, "imageScanFindings.enhancedFindings"):
            return False

        findings = build_json["imageScanFindings"]["enhancedFindings"]

        for finding in findings:
            if "packageVulnerabilityDetails" not in finding:
                continue

            vulnerability_id = misc.find_cve(
                finding["packageVulnerabilityDetails"]["vulnerabilityId"])

            # Not all vulns AWS reports on have CVEs
            if not vulnerability_id:
                log.debug(
                    "%s is not a CVE number" %
                    finding["packageVulnerabilityDetails"]["vulnerabilityId"])
                continue

            if "vendorSeverity" not in finding["packageVulnerabilityDetails"]:
                vulnerability_severity = None
            else:
                vulnerability_severity = finding["packageVulnerabilityDetails"]["vendorSeverity"]

            if not vulnerability_severity or vulnerability_severity.lower() not in self.data:
                vulnerability_id = finding["packageVulnerabilityDetails"]["vulnerabilityId"]
                log.warning(
                    "Uknown vulnerability severity for: %s" %
                    vulnerability_id)
                self.data["unknown"].append(vulnerability_id)
                continue

            self.data[vulnerability_severity.lower()].append(vulnerability_id)

        self.read_complete = True
        return True

    def _parse_sev(self, log_line: str) -> str:
        for sev in self.sev_levels:
            if sev in self.data and sev in log_line:
                return sev

        return False

# End File: automox/src/pignus/parse/parse_aws.py
