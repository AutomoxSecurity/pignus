"""Base Cli

"""
from rich.console import Console
from rich import print

from pignus.client.rest import Rest as PignusRest
from pignus import misc


class CliBase:
    def __init__(self, cli_parser):
        self.cli_parser = cli_parser
        self.route_options = {}
        self.api = PignusRest()
        self.console = Console()
        self.clusters = {}
        self.args = {}

    def run(self):
        self.cli_parser.route_options = self.route_options
        self.args = self.cli_parser.parse()
        if self.args["verb"] == "get" and self.args["subject"][-1:] == "s":
            self.collection()
        elif self.args["verb"] == "search":
            self.search()
        elif self.args["verb"] == "get":
            self.get()
        elif self.args["verb"] == "create":
            self.create()
        elif self.args["verb"] == "edit":
            self.edit()
        elif self.args["verb"] == "delete":
            self.delete()
        return True

    def get(self):
        print("ERROR: %s does not have get." % self.args["subject"])
        exit(1)

    def edit(self):
        print("ERROR: %s does not have edit." % self.args["subject"])
        exit(1)

    def delete(self):
        print("ERROR: %s does not have delete." % self.args["subject"])
        exit(1)

    def collection(self):
        print("ERROR: %s does not have a collection." % self.args["subject"])
        exit(1)

    def search(self):
        print("ERROR: %s does not have search." % self.args["subject"])
        exit(1)

    def get_roles(self) -> dict:
        """Get all RBAC Roles from the Pignus Api.
        :unit-test: TestCliBase.test__get_roles
        """
        response_roles = self.api.roles_get()
        response_json_roles = response_roles.json()
        roles = self.api.objects(response_json_roles)
        ret = {}
        for role in roles:
            ret[role.id] = role
        return ret

    def get_clusters(self) -> dict:
        """Get all clusters from Pignus and put them in a dictionary keyed on Cluser ID. This is
        used in methods which need Cluster data in order to display properly.
        """
        response = self.api.clusters_get()
        self.handle_error(response)

        response_json = response.json()
        clusters_list = self.api.objects(response_json)
        self.clusters = misc.key_list_on(clusters_list)
        return self.clusters

    def get_operations(self, entity_type: str, entity_id: int) -> list:
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id
        }
        response = self.api.operations_get(payload=payload)
        self.handle_error(response)

        response_json = response.json()
        operations = self.api.objects(response_json)
        return operations

    def run_with_loader(self, some_functions: list, some_args: list = []) -> list:
        """Runs a list of functions supplying them with a corresponding list of args, mainting a
        loader on the CLI as we wait for the requests to be completed, passing back the response
        data in the same order which we were asked to fetch it.
        """
        function_output = []
        tasks = [1]
        count = 0
        with self.console.status("[bold green]Loading...\n"):
            while tasks:
                for some_function in some_functions:
                    if some_args:
                        function_output.append(some_function(**some_args[count]))
                    else:
                        function_output.append(some_function())
                    count += 1
                break
        return function_output

    def handle_error(self, response, payload: dict = {}):
        if response.status_code == 404:
            print("[yellow bold]WARNING[/yellow bold]: Not found in %s\n" % self.args["subject"])
            exit(0)
        if response.status_code == 403:
            print("[red bold]ERORR[/red bold]: Not authorized for %s\n" % response.url)
            exit(1)
        if response.status_code == 401:
            response_json = response.json()
            print("[red bold]ERORR[/red bold]: %s\n" % response_json["message"])
            exit(1)
        elif response.status_code > 399:
            print("[red bold]ERORR[/red bold]: %s Could not fetch url %s from Pignus" % (
                response.status_code, response.url))
            if self.args["options"]["debug"]:
                print("Debug")
                print("\tStatus:\t%s" % response.status_code)
                print("\tUrl:\t%s" % response.request.url)
                print("\tMethod:\t%s" % response.request.method)
                print("\t%s" % response.text)
            exit(1)
        return True

    def interactive_bool(self, question: str) -> bool:
        """Run an interactive check forcing the user to type "yes" in order to continue, unless the
        --apply option was used.
        """
        if self.args["options"]["apply"]:
            return True
        print(question)
        response = input("\t> ")
        if response != "yes":
            print("Aborting")
            print("\n")
            exit()
        print("\n")
        return True

    def interactive_value(self, question: str) -> bool:
        """Run an interactive check forcing the user to type "yes" in order to continue, unless the
        --apply option was used.
        """
        response = input("%s\t> " % question)
        return response

    def collection_payload(self) -> dict:
        """Get generic options for a collection payload."""
        payload = {}
        if self.args["options"]["page"]:
            payload["page"] = self.args["options"]["page"]
        if self.args["options"]["limit"]:
            payload["per_page"] = self.args["options"]["limit"]
        return payload

    def fmt_row(self, header, value) -> bool:
        value = str(value)
        print(f"  [bold]{header}[/bold]\t{value}")
        # print("\t[bold]{:<10s}{:>4s}[/bold]{value}".format(header, str(value)))
        return True

    def fmt_header(self, header: str, count: int = None):
        header_print = "[bold underline]%s[/bold underline]" % header
        if count:
            header_print += " - %s" % count
        print(header_print)
        return True

    def fmt_table(self, data: list, pad_front_request: int = 1) -> bool:
        """Format a set of data for the console."""
        longest_header = 0
        for d in data:
            if len(d[0]) > longest_header:
                longest_header = len(d[0])

        fmt_pad_front_count = 1
        pad_front = "\t"
        while fmt_pad_front_count < pad_front_request:
            pad_front += "\t"
            fmt_pad_front_count += 1

        spacing = "\t"
        for d in data:
            if not d:
                row_head = None
            else:
                row_head = d[0]
            if len(d) >= 2:
                row_value = d[1]
            else:
                row_value = None
            if longest_header - len(row_head) > 4:
                spacing = "\t\t"
            elif len(row_head) < 8:
                spacing = "\t\t"
            else:
                spacing = "\t"
            if row_value:
                print("%s[bold]%s[/bold]%s%s" % (pad_front, row_head, spacing, row_value))
            else:
                print("%s[bold]%s[/bold]" % (pad_front, row_head))
        return True


# End File: automox/pignus/src/pignus/cli/base.py
