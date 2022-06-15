"""CLI Details
Provides details on Pignus

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliDetails(CliBase):

    def collection(self) -> bool:
        """Get Pignus details."""
        response = self.api.details_get()
        response_json = response.json()
        print("[bold]Environment[/bold]\t%s" % response_json["data"]["details"]["environment"])
        print("[bold]Url[/bold]\t\t%s" % self.api.api_url)
        print("[bold]Clusters - %s[/bold]" % (
            len(response_json["data"]["details"]["cluster"]["clusters"])))
        for cluster in response_json["data"]["details"]["cluster"]["clusters"]:
            print("\t[bold]%s[/bold]" % cluster["name"])
            print("\t\tID:\t\t%s" % cluster["id"])
            print("\t\tEnabled:\t%s" % cluster["enabled"])
            print("\t\tLast Check-In:\t%s" % cluster["last_check_in"])
        return True

# End File: automox/pignus/src/pignus/cli/cli_details.py
