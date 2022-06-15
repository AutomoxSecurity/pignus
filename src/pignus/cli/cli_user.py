"""
"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc


class CliUser(CliBase):

    def __init__(self, cli_parser):
        super(CliUser, self).__init__(cli_parser)
        self.route_options = {
            "get user": {
                "name": ["--name", "-n"],
                "id": ["--id", "-i"],
            },
            "edit user": {
                "id": ["--id", "-i"],
                "field": ["--field", "-f", "*type_dict"]
            },
            "delete user": {
                "id": ["--id", "-i"],
            }
        }

    def get(self) -> bool:
        """Get information on a specfic User of Pignus."""
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["value"]:
            payload["name"] = self.args["value"]

        operations = [self.api.user_get]
        args = [{"payload": payload}]
        results = self.run_with_loader(operations, args)
        response = results[0]
        self.handle_error(response)

        response_json = response.json()
        user = self.api.objects(response_json)
        # roles = self._get_roles()

        print("User - [bold]%s[/bold]" % user.name)
        print("\t[bold]ID[/bold]\t\t%s" % user.id)
        print("\t[bold]Role ID[/bold]\t\t%s" % user.role_id)
        print("\t[bold]Created[/bold]\t\t%s" % client_misc.fmt_date(user.created_ts))
        print("\t[bold]Last Login[/bold]\t%s" % client_misc.fmt_date(user.last_login))
        print("\n")
        return True

    def create(self) -> bool:
        """Create a Pignus User."""
        print("[bold underline]User - Create[/bold underline]")
        name = self.interactive_value("User Name")
        role_id = self.interactive_value("Role ID")
        payload = {
            "name": name,
            "role_id": role_id
        }
        print("[bold]User[/bold]")
        print("\t[bold]%s[/bold]\t%s" % ("Name", name))
        print("\t[bold]%s[/bold]\t%s" % ("Role ID", role_id))
        print("\n")
        self.interactive_bool("Create User?")

        response = self.api.user_post(payload=payload, create=True)
        self.handle_error(response)
        user = self.api.objects(response.json())
        print("[[bold green]SUCCESS[/bold green]] User created: %s" % user)

        # Create the ApiKey
        self.interactive_bool("Create Api-Key?")
        payload = {
            "create": True,
            "user_id": user.id
        }
        response = self.api.api_key_post(payload)
        self.handle_error(response)

        api_key = self.api.objects(response.json())

        print("[[bold green]SUCCESS[/bold green]] ApiKey created: %s" % api_key.key)

        self.api.api_key_post()

        return True

    def edit(self) -> bool:
        """Get information on a specfic User of Pignus."""
        if not self.args["options"]["id"]:
            print("Error, User ID required.")
            exit(1)

        if not self.args["options"]["field"]:
            print("Error: --field required to edit a User.")
            exit(1)

        payload = {}
        payload["id"] = self.args["options"]["id"]

        response = self.api.user_get(payload)

        self.handle_error(response)
        response_json = response.json()

        user = self.api.objects(response_json)

        field = next(iter(self.args["options"]["field"]))
        value = self.args["options"]["field"][field]

        print("User - [bold]%s[/bold]" % user.name)
        print("\t[bold]ID[/bold]\t\t%s" % user.id)
        print("\t[bold]Role ID[/bold]\t\t%s" % user.role_id)
        print("\t[bold]Created[/bold]\t\t%s" % client_misc.fmt_date(user.created_ts))
        print("\t[bold]Last Login[/bold]\t%s" % client_misc.fmt_date(user.last_login))
        print("\n")
        print("Change:")
        print("\t[bold]%s[/bold]\t\t%s" % (field, value))
        self.interactive_bool("Run update?")

        payload = {}
        payload["id"] = user.id
        payload[field] = value
        request = self.api.user_post(user_id=user.id, payload=payload)
        if request.status_code != 201:
            print("Error: Could not edit: %s" % user.name)
            exit(1)
        print("[bold green]Updated Successfully![/bold green]\n")
        return True

    def delete(self) -> bool:
        """Delete a User from Pignus"""
        if not self.args["options"]["id"]:
            print("ERROR: To delete a User supply the User ID.")
            exit(1)

        user_id = self.args["options"]["id"]
        payload = {
            "id": user_id
        }

        response = self.api.user_get(payload)
        self.handle_error(response)

        response_json = response.json()
        user = self.api.objects(response_json)
        print("User - [bold]%s[/bold]" % user.name)
        print("\t[bold]ID[/bold]\t\t%s" % user.id)
        print("\t[bold]Role ID[/bold]\t\t%s" % user.role_id)
        print("\t[bold]Created[/bold]\t\t%s" % client_misc.fmt_date(user.created_ts))
        print("\t[bold]Last Login[/bold]\t%s" % client_misc.fmt_date(user.last_login))

        self.interactive_bool("Delete User?")

        response = self.api.user_delete(user_id=user.id)
        self.handle_error(response)

        print("[green bold][OK][/green bold] User deleted successfully\n")

        return True

    def collection(self) -> bool:
        """Get information on all Users of Pignus."""
        ops = [self.get_roles, self.api.users_get]
        requests = self.run_with_loader(ops)
        roles = requests[0]
        response = requests[1]

        response_json = response.json()
        total_users = response_json["data"]["pages"]["total_objects"]
        users = self.api.objects(response_json)
        print("[bold]Users - %s[/bold]" % total_users)

        for user in users:
            print("\t[bold]%s[/bold]" % user.name)
            print("\t\t[bold]ID[/bold]\t\t%s" % user.id)
            print("\t\t[bold]Role[/bold]\t\t%s" % roles[user.role_id].name)
            print("\t\t[bold]Last Login[/bold]\t%s" % client_misc.fmt_date(user.last_login))
        return True


# End File: automox/pignus/src/pignus/cli/models/cli_user.py
