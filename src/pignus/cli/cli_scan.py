"""CLI Scan
Handles all interactions with the Pignus API for Scan requests.

Testing
    Unit Tests: automox/pignus/tests/unit/cli/test_cli_scan.py


"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc


class CliScan(CliBase):

    def __init__(self, cli_parser):
        super(CliScan, self).__init__(cli_parser)
        self.route_options = {
            "get scan": {
                "id": ["--id", "-i"]
            },
            "get scans": {
                "image_id": ["--image-id"],
                "image_build_id": ["--image-build-id"]
            }
        }

    def get(self):
        """Get information on a single Image from Pignus."""
        payload = {}
        # import ipdb; ipdb.set_trace();
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["options"]["image_id"]:
            payload["image_id"] = self.args["options"]["image_id"]
        elif self.args["options"]["image_build_id"]:
            payload["image_build_id"] = self.args["options"]["image_build_id"]

        response = self.api.scan_get(payload=payload)
        self.handle_error(response, payload)

        response_json = response.json()
        scan = self.api.objects(response_json)

        response_image = self.api.image_get(image_id=scan.image_id)
        self.handle_error(response_image)
        response_image_json = response_image.json()
        image = self.api.objects(response_image_json)

        print("[bold]Scan - %s[/bold]" % scan.id)
        print("\t[bold]ID[/bold]\t\t\t%s" % scan.id)
        print("\t[bold]Image ID[/bold]\t\t%s" % scan.image_id)
        print("\t[bold]Image Name[/bold]\t\t%s" % image.name)
        print("\t[bold]Image Build ID[/bold]\t\t%s" % scan.image_build_id)
        print("\t[bold]Started[/bold]\t\t\t%s" % client_misc.fmt_date(scan.created_ts))
        print("\t[bold]Completed[/bold]\t\t%s" % client_misc.fmt_date(scan.ended_ts))
        print("\t[bold]Scanner ID[/bold]\t\t%s" % scan.scanner_id)
        print("\t[bold]Operation ID[/bold]\t\t%s" % scan.operation_id)

        print("\t[bold]Security[/bold]")
        if scan.cve_critical_nums:
            print("\t\t[bold]CVEs Critical[/bold] - %s" % scan.cve_critical_int)
            print("\t\t\t%s" % client_misc.fmt_list(scan.cve_critical_nums))

        if scan.cve_high_nums:
            print("\t\t[bold]CVEs High[/bold] - %s" % scan.cve_high_int)
            print("\t\t\t%s" % client_misc.fmt_list(scan.cve_high_nums))

        if scan.cve_medium_nums:
            print("\t\t[bold]CVEs Medium[/bold] - %s" % scan.cve_medium_int)
            print("\t\t\t%s" % client_misc.fmt_list(scan.cve_medium_nums))

        if scan.cve_low_nums:
            print("\t\t[bold]CVEs Low[/bold] - %s" % scan.cve_low_int)
            print("\t\t\t%s" % client_misc.fmt_list(scan.cve_low_nums))

        print("\n")
        # return image

    def collection(self) -> bool:
        """Get information on all Scan of Pignus."""
        payload = self.collection_payload()
        if self.args["options"]["image_id"]:
            payload["image_id"] = self.args["options"]["image_id"]
        elif self.args["options"]["image_build_id"]:
            payload["image_build_id"] = self.args["options"]["image_build_id"]

        if self.args["options"]["limit"]:
            payload["per_page"] = self.args["options"]["limit"]
        else:
            payload["per_page"] = 5

        response = self.api.scans_get(payload)
        self.handle_error(response)

        response_scanners = self.api.scanners_get()
        self.handle_error(response_scanners)
        scanners = self.api.objects(response_scanners.json())
        print(scanners)
        # import ipdb; ipdb.set_trace();

        response_json = response.json()
        total_scans = response_json["data"]["pages"]["total_objects"]
        if response_json["data"]["pages"]:
            per_page = response_json["data"]["pages"]["per_page"]
            page = response_json["data"]["pages"]["current_page"]
            last_page = response_json["data"]["pages"]["last_page"]

        scans = self.api.objects(response_json)
        print("[bold]Scans - %s[/bold]" % total_scans)
        if not scans:
            return

        print("\t[bold]Page[/bold]\t\t%s" % page)
        print("\t[bold]Last Page[/bold]\t%s" % last_page)
        print("\t[bold]Per Page[/bold]\t%s" % per_page)
        print("\n")

        for scan in scans:
            self.fmt_row("ID", scan.id)
            self.fmt_row("\tImage ID", scan.image_id)
            self.fmt_row("\tImage Build ID", scan.image_build_id)

            if not scan.ended_ts:
                self.fmt_row("\tStarted", client_misc.fmt_date(scan.created_ts))
            else:
                self.fmt_row("\tCompleted", client_misc.fmt_date(scan.ended_ts))
            if scan.cve_critical_int:
                print("\t[bold]CVEs - Critical[/bold]\t[red bold]%s[/red bold]" % scan.cve_critical_int)
                # print("\t\t%s" % client_misc.fmt_list(scan.cve_critical_nums))
            if scan.cve_high_int:
                print("\t[bold]CVEs - High[/bold]\t[red bold]%s[/red bold]" % scan.cve_high_int)
                # print("\t\t%s" % client_misc.fmt_list(scan.cve_high_nums))
            if scan.cve_medium_int:
                print("\t[bold]CVEs - Medium[/bold]\t[red bold]%s[/red bold]" % scan.cve_medium_int)
                # print("\t\t%s" % client_misc.fmt_list(scan.cve_medium_nums))
            if scan.cve_low_int:
                print("\t[bold]CVEs - Low[/bold]\t[bold]%s[/bold]" % scan.cve_low_int)
                # print("\t\t%s" % client_misc.fmt_list(scan.cve_low_nums))
            if scan.cve_unknown_int:
                print("\t[bold]CVEs - Unknown[/bold]\t[bold]%s[/bold]" % scan.cve_unknown_int)
                # print("\t\t%s" % client_misc.fmt_list(scan.cve_unknown_nums))
        print("\n")
        return True


# End File: automox/pignus/src/pignus/cli/cli_scan.py
