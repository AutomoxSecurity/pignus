"""CLI RolePerm
Handles all interactions with the Pignus API for RolePerm requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus import misc


class CliRolePerm(CliBase):

    def collection(self) -> bool:
        """Get all Roles Perms."""
        payload = {}
        if self.args["options"]["role_id"]:
            payload["role_id"] = self.args["options"]["role_id"]

        response = self.api.role_perms_get(payload)
        self.handle_error(response)

        response_json = response.json()
        role_perms = self.api.objects(response_json)

        # Get Roles
        roles_response = self.api.roles_get()
        self.handle_error(roles_response)
        roles_response_json = roles_response.json()
        roles = self.api.objects(roles_response_json)
        roles = misc.key_list_on(roles)

        # Get Perms
        perms_response = self.api.perms_get({"per_page": 100})
        self.handle_error(perms_response)
        perms_response_json = perms_response.json()
        perms = self.api.objects(perms_response_json)
        perms = misc.key_list_on(perms)

        print("[bold underline]Roles Perms - %s[/bold underline]" % len(role_perms))
        for role_perm in role_perms:
            print("[bold]ID[/bold] - %s" % role_perm.id)
            print("\t[bold]Role[/bold]\t\t%s" % roles[role_perm.role_id].name)
            print("\t[bold]Perm Name[/bold]\t%s" % perms[role_perm.perm_id].name)

        return True

# End File: automox/pignus/src/pignus/cli/cli_role_perm.py
