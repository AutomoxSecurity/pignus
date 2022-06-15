"""CLI Cve

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliCve(CliBase):

    def get(self) -> bool:
        if "value" not in self.args or not self.args["value"]:
            print("[red bold]ERROR:[/red bold] get cluster requires a Cluster name to be supplied.")
            exit(1)
        cve_number = self.args["value"]
        payload = {
            "number": self.args["value"]
        }

        response = self.api.cve_get(payload)
        self.handle_error(response)

        response_json = response.json()
        images = self.api.objects(response_json)
        cve_sev = None
        num_image_builds = 0

        for image in images:
            for image_build_digest, image_build in image.builds.items():
                for scan in image_build.scans:
                    if scan["cve_critical_nums"] and cve_number in scan["cve_critical_nums"]:
                        num_image_builds += 1
                        cve_sev = "critical"
                    if scan["cve_high_nums"] and cve_number in scan["cve_high_nums"]:
                        num_image_builds += 1
                        cve_sev = "high"
                    if scan["cve_medium_nums"] and cve_number in scan["cve_medium_nums"]:
                        num_image_builds += 1
                        cve_sev = "medium"
                    if scan["cve_low_nums"] and cve_number in scan["cve_low_nums"]:
                        num_image_builds += 1
                        cve_sev = "low"
                    if scan["cve_unknown_nums"] and cve_number in scan["cve_unknown_nums"]:
                        num_image_builds += 1
                        cve_sev = "unknown"

        print("%s" % cve_number)
        if cve_sev in ["critical", "high"]:
            cve_sev_msg = "[red bold]%s[/red bold]" % cve_sev.upper()
        elif cve_sev in ["medium", "low"]:
            cve_sev_msg = "[yellow bold]%s[/yellow bold]" % cve_sev.upper()
        else:
            cve_sev_msg = cve_sev.upper()
        print("\tSeverity:\t%s" % cve_sev_msg)
        print("\tDetails\t%s" % "https://nvd.nist.gov/vuln/detail/%s" % cve_number)
        print("\tImages with CVE\t%s" % len(images))
        print("Clusters with CVE%s" % "")
        print(num_image_builds)
        return True

# End File: automox/pignus/src/pignus/cli/cli_cve.py
