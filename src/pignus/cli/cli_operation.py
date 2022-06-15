"""CLI Operation
Handles all interactions with the Pignus API for Operation requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus.models.operation import Operation
from pignus.utils import client_misc


class CliOperation(CliBase):

    def __init__(self, cli_parser):
        super(CliOperation, self).__init__(cli_parser)
        self.route_options = {
            "get operation": {
                "id": ["--id", "-i"],
            },
            "delete operation": {
                "id": ["--id", "-i"],
            },
            "get operations": {
                "type": ["--type"],
                "image_build_id": ["--image-build-id", "-ibi"],
            },
        }

    def get(self) -> bool:
        """Get information on a specfic Operation of Pignus."""
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]

        response = self.api.operation_get(payload)
        self.handle_error(response)

        response_json = response.json()
        operation = self.api.objects(response_json)

        entity = None
        if operation.entity_type == "image_builds":
            response_image_build = self.api.image_build_get(image_build_id=operation.entity_id)
            self.handle_error(response_image_build)

            response_image_build_json = response_image_build.json()
            entity = self.api.objects(response_image_build_json)

        print("[bold]Operation - %s[/bold]" % operation.id)

        operation_details = []
        operation_details.append(["Type", operation.type])
        if operation.sub_type:
            operation_details.append(["Sub-Type", operation.sub_type])
        if entity:
            operation_details.append(["Entity", entity])

        operation_details.append(["Entity-Type", operation.entity_type])
        operation_details.append(["CodeBuild ID", operation.build_id])
        operation_details.append(["Started", client_misc.fmt_date(operation.start_ts)])
        operation_details.append(["Ended", client_misc.fmt_date(operation.end_ts)])
        operation_details.append(["Result", operation.result])
        operation_details.append(["Message", operation.message])
        self.fmt_table(operation_details)
        return True

    def delete(self) -> bool:
        """Delete an Operation from Pignus"""
        if not self.args["options"]["id"]:
            print("ERROR: To delete an Operation supply the Operation ID.")
            exit(1)

        operation_id = self.args["options"]["id"]
        payload = {
            "id": operation_id
        }

        response = self.api.operation_get(payload)
        self.handle_error(response)

        response_json = response.json()
        user = self.api.objects(response_json)

        self.interactive_bool("Delete User?")

        response = self.api.user_delete(user_id=user.id)
        self.handle_error(response)

        print("[green bold][OK][/green bold] User deleted successfully\n")

        return True

    def collection(self) -> bool:
        """Get Operations run by Pignus."""
        payload = {}
        if self.args["options"]["page"]:
            payload["page"] = self.args["options"]["page"]
        if self.args["options"]["limit"]:
            payload["per_page"] = self.args["options"]["limit"]
        if self.args["options"]["image_build_id"]:
            payload["entity_id"] = self.args["options"]["image_build_id"]
            payload["entity_type"] = "image_builds"
        if self.args["options"]["type"]:
            payload["type"] = self.args["options"]["type"]

        response = self.api.operations_get(payload)
        self.handle_error(response)
        response_json = response.json()

        total = response_json["data"]["pages"]["total_objects"]
        per_page = response_json["data"]["pages"]["per_page"]
        page = response_json["data"]["pages"]["current_page"]
        last_page = response_json["data"]["pages"]["last_page"]
        operations = self.api.objects(response_json)

        print("[bold underline]Operations - %s[/bold underline]" % total)
        print("\tPage:\t\t%s" % page)
        print("\tLast Page:\t%s" % last_page)
        print("\tPer Page:\t%s" % per_page)
        print("\n")
        for operation in operations:
            print("[bold]%s[/bold]" % operation.id)
            print("\t[bold]Operation[/bold]\t%s" % operation.type)
            if operation.sub_type:
                print("\t[bold]Scanner[/bold]\t%s" % operation.sub_type)
            print("\t[bold]Entity[/bold]\t\t%s" % operation.entity_type)
            print("\t[bold]Entity ID[/bold]\t%s" % operation.entity_id)
            print("\t[bold]Result[/bold]\t\t%s" % operation.result)
            if operation.message:
                print("\t[bold]Message[/bold]\t\t%s" % operation.message)
            print("\t[bold]Started[/bold]\t\t%s" % client_misc.fmt_date(operation.start_ts))
            print("\t[bold]Ended[/bold]\t\t%s" % client_misc.fmt_date(operation.end_ts))

        return True

    def _display_operation(self, operation: Operation) -> bool:
        print("Operation - [bold]%s[/bold]" % operation.name)
        print("\t[bold]ID[/bold]\t\t%s" % operation.id)
        print("\n")
        return True

# End File: automox/pignus/src/pignus/cli/cli_operation.py
