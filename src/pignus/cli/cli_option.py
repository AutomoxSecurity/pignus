"""CLI Option
Handles all interactions with the Pignus API for Option requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase
# from pignus.utils import client_misc


class CliOption(CliBase):

    def get(self) -> bool:
        payload = {}
        if self.args["value"]:
            payload["option_str"] = self.args["value"]

        response = self.api.option_get(**payload)
        response_json = response.json()
        option = self.api.objects(response_json)
        print("[bold]%s[/bold]\t%s" % (option.name, option.value))

    def edit(self) -> bool:
        payload = {}
        if self.args["value"]:
            payload["option_str"] = self.args["value"]

        response = self.api.option_get(**payload)
        response_json = response.json()
        option = self.api.objects(response_json)
        print("[bold]%s[/bold]\t%s" % (option.name, option.value))

        value = self.interactive_value("Value?")
        print(value)
        self.interactive_bool("Run update?")
        payload = {
            "value": [value]
        }
        response = self.api.option_post(option.id, payload)
        self.handle_error(response)

        print(response)

    def collection(self) -> bool:
        """Get information on all Options of Pignus."""
        response = self.api.options_get()
        if response.status_code != 200:
            print("ERORR: Could not fetch /options from Pignus")
            exit(1)

        response_json = response.json()
        options = response_json["data"]["objects"]

        print("[bold]Options[/bold] - %s" % len(options))
        for option_name, option_info in options.items():
            print("\t[bold]%s[/bold]\t\t%s" % (option_name, option_info["value"]))
        print("\n")
        return True

# End File: automox/pignus/src/pignus/cli/cli_option.py
