"""CLI Perm
Handles all interactions with the Pignus API for Perm requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliPerm(CliBase):

    def collection(self) -> bool:
        """Get all Pignus Perms."""
        response = self.api.perms_get()
        self.handle_error(response)

        if response.status_code != 200:
            print("ERORR: Could not fetch /roles from Pignus")
            exit(1)
        response_json = response.json()
        perms = self.api.objects(response_json)
        print("[bold underline]Perms - %s[/bold underline]" % len(perms))
        for perm in perms:
            print("[bold]%s[/bold]" % perm.name)
            print("\tID:\t%s" % perm.id)
        return True

# End File: automox/pignus/src/pignus/cli/cli_perm.py
