"""Parse Crowdstrike Scan Logs

"""
from pignus.parse.parse_cloudwatch_base import ParseCloudWatchBase


class ParseCrowdstrike(ParseCloudWatchBase):

    def __init__(self):
        super(ParseCrowdstrike, self).__init__()
        self.start_line = "Searching for vulnerabilities in scan report"
        self.end_line = "Entering phase POST_BUILD"
        self.catch_errors = [
            "AccessDeniedException",
            "cs_scanimage.py: error",
            "docker.errors.APIError: 500 Server Error",
        ]

    def parse_line(self, cve_line: str) -> bool:
        """
        WARNING HIGH     CVE-2005-2541    Vulnerability detected affecting tar 1.30+dfsg-6
        """
        finding = False
        if "WARNING " not in cve_line:
            return False

        for sev_level in self.sev_levels:
            key_phrase = "WARNING %s" % sev_level.upper()
            if key_phrase in cve_line:
                tmp = cve_line[cve_line.find("CVE-"):]
                cve_number = tmp[: tmp.find(" ")]
                self.data[sev_level].append(cve_number)
                finding = True
        return finding


# End File: automox/src/pignus/parse/parse_crowdstrike.py
