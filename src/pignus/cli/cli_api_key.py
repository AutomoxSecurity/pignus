"""CLI Api Key
Handles all interactions with the Pignus API for ApiKey requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc
from pignus import misc


class CliApiKey(CliBase):

    def __init__(self, cli_parser):
        """Set the CLiApiKey's CLI options.
        :unit-test: TestCliApiKey::test____init__
        """
        super(CliApiKey, self).__init__(cli_parser)
        self.route_options = {
            "get api-key": {
                "id": ["--id", "-i"],
                "user_id": ["--user-id", "-uid"]
            },
            "delete api-key": {
                "id": ["--id", "i"]
            },
            "get api-keys": {
                "user_id": ["--user-id", "-uid"]
            }
        }

    def get(self) -> bool:
        """Get information on a single Cluster from Pignus."""
        if not self.args["options"]["id"]:
            print("[red bold]ERROR:[/red bold] get api-key requires a api key ID to be supplied.")
            exit(1)

        response = self.api.api_key_get(api_key_id=self.args["options"]["id"])
        self.handle_error(response)

        api_key = self.api.objects(response.json())
        self._display_api_key(api_key)

        # Display the api key clear
        self.interactive_bool("Display Key?")
        response = self.api.api_key_get(api_key_id=api_key.id, payload={"show-key": True})
        self.handle_error(response)

        open_key = self.api.objects(response.json())

        print(open_key.key)
        print("\n")
        return True

    def create(self) -> bool:
        """Create a Pignus Api-Key."""
        print("[boldApi Key[/bold] - Create")
        user_id = self.interactive_value("User ID")
        payload = {
            "user_id": user_id
        }
        print("[bold]Api-Key[/bold]")
        print("\t[bold]%s[/bold]\t%s" % ("User ID", user_id))
        print("\n")
        self.interactive_bool("Create Api-Key?")

        response = self.api.api_key_post(payload=payload, create=True)
        self.handle_error(response)

        print("[[bold green]SUCCESS[/bold green]] Api-Key created successfully.")
        api_key = self.api.objects(response.json())
        self._display_api_key(api_key)
        return True

    def delete(self) -> bool:
        """Delete an ApiKey from Pignus"""
        if not self.args["options"]["id"]:
            print("ERROR: To delete an Api Key supply the Api Key ID.")
            exit(1)

        api_key_id = self.args["options"]["id"]
        payload = {
            "id": api_key_id
        }

        response = self.api.api_key_get(payload=payload)
        self.handle_error(response)

        response_json = response.json()
        api_key = self.api.objects(response_json)
        self._display_api_key(api_key)

        self.interactive_bool("Delete Api Key?")

        response = self.api.api_key_delete(api_key_id=api_key.id)
        self.handle_error(response)

        print("[green bold][OK][/green bold] Api Key deleted successfully\n")

        return True

    def collection(self) -> bool:
        """Get a collection of Api-Keys as well as Users so we can pair user_ids to actual Users
        that they belong too.
        """
        payload = {}
        if self.args["options"]["user_id"]:
            payload["user_id"] = self.args["options"]["user_id"]
            response_users = self.api.user_get(user_id=payload["user_id"])
            self.handle_error(response_users)
            response_users_json = response_users.json()
            users = [self.api.objects(response_users_json)]
        else:
            response_users = self.api.users_get()
            self.handle_error(response_users)
            response_users_json = response_users.json()
            users = self.api.objects(response_users_json)

        users = misc.key_list_on(users, "id")

        response = self.api.api_keys_get(payload=payload)
        self.handle_error(response)

        response_json = response.json()
        api_keys = self.api.objects(response_json)

        print("[bold]Api Keys[/bold] - %s" % len(api_keys))
        for api_key in api_keys:
            if api_key.user_id in users:
                user_name = users[api_key.user_id].name
            else:
                user_name = None
            print("\t[bold]ID:[/bold]\t\t%s" % api_key.id)
            print("\t\t[bold]User Name[/bold]\t%s" % user_name)
            print("\t\t[bold]Last Use[/bold]\t%s" % (client_misc.fmt_date(api_key.last_use)))
            print("\t\t[bold]Created[/bold]\t\t%s" % client_misc.fmt_date(api_key.created_ts))
            print("\t\t[bold]Enabled[/bold]\t\t%s" % api_key.enabled)
            print("\t\t[bold]Expires[/bold]\t%s" % client_misc.fmt_date(api_key.expiration))
            print("\n")
        return True

    def _display_api_key(self, api_key) -> bool:
        """Display a given ApiKey to the CLI.
        :unit-test: TestCliApiKey::test___display_api_key
        """
        print("\t[bold]ID:[/bold]\t\t%s" % api_key.id)
        print("\t\tUser ID:\t%s" % api_key.user_id)
        if api_key.key:
            print("\t\tKey:\t%s" % api_key.key)
        print("\t\tLast Use:\t%s" % (client_misc.fmt_date(api_key.last_use)))
        print("\t\tCreated:\t%s" % client_misc.fmt_date(api_key.created_ts))
        print("\t\tEnabled:\t%s" % api_key.enabled)
        print("\t\tExpires:\t%s" % client_misc.fmt_date(api_key.expiration))
        print("\n")
        return True

# End File: automox/pignus/src/pignus/cli/cli_api_key.py
