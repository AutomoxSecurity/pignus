"""CLI Role
Handles all interactions with the Pignus API for Role requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliRole(CliBase):

    def collection(self) -> bool:
        """Get all Roles."""
        response = self.api.roles_get()
        self.handle_error(response)

        response_json = response.json()
        roles = self.api.objects(response_json)

        print("[bold underline]Roles - %s[/bold underline]" % len(roles))
        for role in roles:
            print("[bold]%s[/bold]" % role.name)
            print("\tID:\t%s" % role.id)
        return True

# End File: automox/pignus/src/pignus/cli/cli_role.py
