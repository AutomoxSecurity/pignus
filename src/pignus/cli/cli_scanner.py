"""CLI Scanner
Handles all interactions with the Pignus API for Scanner requests.

Testing
    Unit Tests: automox/pignus/tests/unit/cli/test_cli_scanner.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliScanner(CliBase):

    def __init__(self, cli_parser):
        super(CliScanner, self).__init__(cli_parser)
        self.route_options = {
            "get scanner": {
                "id": ["--id", "-i"],
            },
            "edit scanner": {
                "id": ["--id", "-i"],
            },
        }

    def get(self):
        """Get information on a single Image from Pignus."""
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["value"]:
            payload["name"] = self.args["value"]

        operations = [self.api.scanner_get]
        args = [{"payload": payload}]
        results = self.run_with_loader(operations, args)
        response = results[0]
        self.handle_error(response, payload)

        response_json = response.json()
        scanner = self.api.objects(response_json)

        print("Scanner")
        print("\tID:\t%s" % scanner.id)
        print("\tName:\t%s" % scanner.name)
        print("\tEnabled:\t%s" % scanner.enabled)
        print("\n")

    def edit(self) -> bool:
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["value"]:
            payload["name"] = self.args["value"]

        operations = [self.api.scanner_get]
        args = [{"payload": payload}]
        results = self.run_with_loader(operations, args)
        response = results[0]
        self.handle_error(response, payload)
        response_json = response.json()
        scanner = self.api.objects(response_json)

        value = self.interactive_value("Enabled?")
        payload = {
            "id": scanner.id,
            "enabled": value
        }
        print(value)
        self.interactive_bool("Run Update?")
        print(value)
        self.interactive_bool("Run update?")
        response = self.api.scanner_post(payload)
        self.handle_error(response)
        print(response)

    def collection(self) -> bool:
        """Get information on all Scanners of Pignus."""
        response = self.api.scanners_get()
        self.handle_error(response)

        response_json = response.json()
        total_scanners = response_json["data"]["pages"]["total_objects"]
        scanners = self.api.objects(response_json)
        self.fmt_header("Scanners", total_scanners)

        scanners_data = []
        for scanner in scanners:
            scanners_data.append([scanner.name])
            scanners_data.append(["ID", scanner.id])
            if scanner.enabled:
                scanners_data.append(["Enabled", scanner.enabled])
            else:
                scanners_data.append(["Enabled", "[red]False[/red]"])
            scanners_data.append([""])
        self.fmt_table(scanners_data)
        print("\n")
        return True

# End File: automox/pignus/src/pignus/cli/cli_scanner.py
