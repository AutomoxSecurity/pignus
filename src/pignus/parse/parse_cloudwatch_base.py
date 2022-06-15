"""Parse CloudWatch Base

"""
from pignus.models.image import Image


class ParseCloudWatchBase:

    def __init__(self):
        self.start_line = None
        self.end_line = None
        self.catch_errors = []
        self.sev_levels = ["critical", "high", "medium", "low", "negligible"]
        self.data = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "unknown": [],
            "errors": []
        }
        self.completed_successfully = False
        self.parse_json = False
        self.read_complete = False
        self.image = None

    def parse(self, image: Image, build_logs: list):
        """Parse a list of CloudWatch logs."""
        start_line_number = self.find_start_line(build_logs)
        self.logs = build_logs
        self.count = start_line_number
        for log in self.logs[start_line_number:]:

            # Find common known error lines.
            for catch_error in self.catch_errors:
                if catch_error in log["message"]:
                    self.data["errors"].append(log["message"])
                    continue

            if self.parse_json:
                self.decode_json(log["message"])
            else:
                self.parse_line(log["message"])

            # Check if we're at the end of the log section we want to read
            if self.read_complete:
                break
        self.data["completed_successfully"] = True
        return self.data

    def find_start_line(self, build_logs: list) -> int:
        """Get the first line of the log that's worth reading."""
        if not self.start_line:
            return 0
        key = self.start_line
        c = 0
        cve_detail_line = None
        for log in build_logs:
            c += 1
            if key in log["message"]:
                if "echo" in log["message"]:
                    continue
                cve_detail_line = c
                break
        return cve_detail_line

    def find_end_line(self, log_message: str) -> bool:
        """Checks to see if a line matches the given self.end_line for a parser. """
        if not self.end_line:
            return False
        if self.end_line in log_message:
            return True
        else:
            return False

    def parse_line(self, log_message: str) -> None:
        return None

# End File: automox/src/pignus/parse/parse_cloudwatch_base.py
