"""CLI ImageBuild
Handles all interactions with the Pignus API for ImageBuild requests.

"""
from rich import print

from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.models.scan import Scan
from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc


class CliImageBuild(CliBase):

    def __init__(self, cli_parser):
        super(CliImageBuild, self).__init__(cli_parser)
        self.route_options = {
            "get image-build": {
                "digest": ["--digest", "-d"],
                "id": ["--id", "-i"],
            },
            "edit image-build": {
                "id": ["--id", "-i"],
            },
        }

    def get(self):
        """Get information on a single ImageBuild from Pignus."""
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["value"]:
            payload["digest"] = self.args["value"]

        response = self.api.image_build_get(payload=payload)
        self.handle_error(response, payload)

        response_json = response.json()
        image_build = self.api.objects(response_json)

        payload = {
            "id": image_build.image_id
        }
        response_image = self.api.image_get(payload=payload)

        self.handle_error(response_image)

        response_image_json = response_image.json()
        image = self.api.objects(response_image_json)

        self._display_image_build(image, image_build)

        print("\n")
        return True

    def edit(self) -> bool:
        """Edit an ImageBuild. """
        if not self.args["options"]["id"]:
            print("Error, ImageBuild ID required.")
            exit(1)

        payload = {}
        payload["id"] = self.args["options"]["id"]

        response = self.api.image_build_get(payload=payload)
        self.handle_error(response)

        response_json = response.json()
        image_build = self.api.objects(response_json)
        print(image_build)
        sync_flag = self.interactive_value("Flag Sync")
        scan_flag = self.interactive_value("Flag Scan")

        print("Change:")
        print("Sync Flag: %s" % sync_flag)
        print("Scan Flag: %s" % scan_flag)
        self.interactive_bool("Run update?")

        if sync_flag:
            payload["sync_flag"] = sync_flag
        if scan_flag:
            payload["scan_flag"] = scan_flag

        response = self.api.image_build_post(payload=payload)
        self.handle_error(response)

        print("SUCCESS")

    def collection(self) -> bool:
        """Get information on all ImageBuilds tracked by Pignus.
        :unit-test: TestCliImageBuild:test__collection
        """
        payload = {}
        if self.args["options"]["page"]:
            payload["page"] = self.args["options"]["page"]
        if self.args["options"]["limit"]:
            payload["per_page"] = self.args["options"]["limit"]

        response = self.api.image_builds_get(payload)
        self.handle_error(response)

        response_json = response.json()
        total = response_json["data"]["pages"]["total_objects"]
        per_page = response_json["data"]["pages"]["per_page"]
        page = response_json["data"]["pages"]["current_page"]
        last_page = response_json["data"]["pages"]["last_page"]
        image_builds = self.api.objects(response_json)

        print("[bold]Image-Builds[/bold] - %s" % total)
        print("\tPage:\t\t%s" % page)
        print("\tLast Page:\t%s" % last_page)
        print("\tPer Page:\t%s" % per_page)
        print("\n")
        for image_build in image_builds:
            print("[bold]%s[/bold]" % image_build.id)
            print("\tTags:\t\t%s" % client_misc.fmt_list(image_build.tags))
            print("\tDigest:\t\t%s" % image_build.digest)
            print("\tImage ID:\t%s" % image_build.image_id)

        return True

    def _display_image_build(self, image: Image, image_build: ImageBuild) -> bool:
        """Prints the ImageBuild to the console.
        """
        print("[bold underline]ImageBuild - %s[/bold underline]" % image_build.digest)
        ib_data = []
        ib_data.append(["ID", image_build.id])
        ib_data.append(["Short Digest", client_misc.fmt_short_digest(image_build.digest)])
        ib_data.append(["Image ID", image_build.image_id])
        ib_data.append(["Image Name", image.name])
        ib_data.append(["Tags", client_misc.fmt_list(image_build.tags)])
        ib_data.append([
            "Repository",
            image_build.repository])

        ib_data.append(["Created", client_misc.fmt_date(image_build.created_ts)])
        ib_data.append(["Maintained", image_build.maintained])

        # ImageBuild Sync job details
        if image_build.sync_last_ts:
            ib_data.append(["Last Sync", client_misc.fmt_date(image_build.sync_last_ts)])
        elif not image_build.sync_enabled:
            ib_data.append(["Sync Status", "[red bold]Disabled[/red bold]"])
        elif image_build.sync_flag:
            ib_data.append(["Flag Sync", "[green bold]True[/green bold]"])

        # ImageBuild Scan job details
        if image_build.scan_flag:
            ib_data.append(["Flag Scan", "[green bold]True[/green bold]"])
        ib_data.append(["Last Scan", client_misc.fmt_date(image_build.scan_last_ts)])
        if not image_build.scan_enabled:
            ib_data.append(["Scan Status", "[red bold]Disabled[/red bold]"])
        self.fmt_table(ib_data)

        # Display Image details
        print("\t[bold underline]Image[/bold underline]")
        image_data = []
        image_data.append(["Image Name", image.name])

        for meta_name, meta in image.metas.items():
            image_data.append(meta_name, meta.value)

        self.fmt_table(image_data, 2)

        # Display ImageBuild Meta

        # Handle Scan
        scan = None
        if image_build.scan:
            scan = Scan()
            scan.build_from_dict(image_build.scan)
            self.display_scan(scan)

        operations = self.get_operations("image_builds", image_build.id)
        num_operations_show = 2
        num_operations_shown = 0
        print("\t[bold underline]Operations - %s[/bold underline]" % len(operations))
        image_build_operations_data = []

        for operation in operations:
            if num_operations_shown == num_operations_show:
                break
            image_build_operations_data.append(["ID", operation.id])
            image_build_operations_data.append(["Type", operation.type])

            if operation.sub_type:
                image_build_operations_data.append(["Sub-Type", operation.sub_type])

            image_build_operations_data.append(["CodeBuild ID", operation.build_id])
            if not operation.end_ts:
                image_build_operations_data.append(["Started", client_misc.fmt_date(operation.start_ts)])
            else:
                image_build_operations_data.append(["Ended", client_misc.fmt_date(operation.end_ts)])

            if operation.result == False:
                operation_result_msg = "[red bold]Failed[/red bold]"
            elif operation.result == True:
                operation_result_msg = "[green bold]Succeeded[/green bold]"
            elif not operation.end_ts:
                operation_result_msg = "[itallic]In Progress[/itallic]"
            else:
                operation_result_msg = None
            image_build_operations_data.append(["Result", operation_result_msg])
            if operation.message:
                image_build_operations_data.append(["Message", operation.message])
            image_build_operations_data.append(["", ""])
            num_operations_shown += 1

        self.fmt_table(image_build_operations_data, 2)

    def display_scan(self, scan: Scan):
        if not scan:
            return
        print("\t[bold underline]Last Scan[/bold underline]")
        scan_data = []
        scan_data.append(["ID", scan.id])
        scan_data.append(["Completed", client_misc.fmt_date(scan.ended_ts)])
        scan_data.append(["Scanner ID", scan.scanner_id])
        scan_data.append(["Operation ID", scan.operation_id])
        scan_data.append(["CodeBuild ID", scan.codebuild_id])

        total_cves = scan.cve_critical_int + scan.cve_high_int + scan.cve_medium_int
        total_cves += scan.cve_low_int + scan.cve_unknown_int

        # Display CVEs
        scan_data.append(["[bold underline]CVEs[/bold underline]", total_cves])
        if scan.cve_critical_int > 0:
            scan_data.append(["\t[bold red]CRITICAL[/bold red]", scan.cve_critical_int])
            scan_data.append(["\t\t", client_misc.fmt_list(scan.cve_critical_nums)])
        else:
            scan_data.append(["\t[bold]CRITICAL[/bold]", scan.cve_critical_int])
        if scan.cve_high_int > 0:
            scan_data.append(["\t[bold red]HIGH[/bold red]", scan.cve_high_int])
            scan_data.append(["\t\t", client_misc.fmt_list(scan.cve_high_nums)])
        else:
            scan_data.append(["\t[bold]HIGH[/bold]", scan.cve_high_int])
        self.fmt_table(scan_data, 2)

        # if scan.ended_ts:
        # image_build_scans_data.append(["Scanner ID", scan.scanner_id])
        # image_build_scans_data.append(["Job Success", scan.scan_job_success])

        # image_build_scans_data.append(["CVES", ""])
        # if scan.cve_critical_int > 0:
        #     reported_cves = True
        #     image_build_scans_data.append(
        #         ["\tCritical", "[red bold]%s[/red bold]" % scan.cve_critical_int])
        #     image_build_scans_data.append(
        #         [
        #             "\t",
        #             "[red bold]%s[/red bold]" % client_misc.fmt_list(scan.cve_critical_nums)
        #         ])
        # if scan.cve_high_int > 0:
        #     reported_cves = True
        #     image_build_scans_data.append(
        #         ["\tHigh", "[red bold]%s[/red bold]" % scan.cve_high_int])
        #     image_build_scans_data.append(
        #         ["\t", "[red bold]%s[/red bold]" % client_misc.fmt_list(scan.cve_high_nums)])

        # if scan.cve_medium_int > 0:
        #     reported_cves = True
        #     image_build_scans_data.append(
        #         ["\tMedium", "[yellow bold]%s[/yellow bold]" % scan.cve_medium_int])
        #     image_build_scans_data.append(
        #         [
        #             "\t",
        #             "[yellow]%s[/yellow]" % client_misc.fmt_list(scan.cve_medium_nums)
        #         ])

        # if scan.cve_low_int > 0:
        #     reported_cves = True
        #     image_build_scans_data.append(
        #         ["\tLow", "[yellow bold]%s[/yellow bold]" % scan.cve_low_int])
        #     image_build_scans_data.append(
        #         [
        #             "\t",
        #             "[yellow bold]%s[/yellow bold]" % client_misc.fmt_list(scan.cve_low_nums)
        #         ])

        # if scan.cve_unknown_int and scan.cve_unknown_int > 0:
        #     reported_cves = True
        #     image_build_scans_data.append(
        #         ["\tUnknown", "[yellow bold]%s[/yellow bold]" % scan.cve_unknown_int])

        #     image_build_scans_data.append(
        #         [
        #             "\t",
        #             "[yellow bold]%s[/yellow bold]" % client_misc.fmt_list(scan.cve_unknown_nums)
        #         ])

        # image_build_scans_data.append(["", ""])


# End File: automox/pignus/src/pignus/cli/cli_image_build.py
