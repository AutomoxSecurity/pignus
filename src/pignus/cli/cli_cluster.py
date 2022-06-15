"""CLI Cluster
Handles all interactions with the Pignus API for Cluster requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc


class CliCluster(CliBase):

    def __init__(self, cli_parser):
        super(CliCluster, self).__init__(cli_parser)
        self.route_options = {
            "delete cluster": {
                "id": ["--id", "-i"],
            }
        }

    def get(self) -> bool:
        """GET information on a single Cluster from Pignus."""
        if "value" not in self.args or not self.args["value"]:
            print("[red bold]ERROR:[/red bold] get cluster requires a Cluster name to be supplied.")
            exit(1)

        response = self.api.cluster_get(cluster_name=self.args["value"])
        self.handle_error(response)

        response_json = response.json()
        cluster = self.api.objects(response_json)
        self._display_cluster(cluster)
        return True

    def create(self) -> bool:
        """Create a Pignus Cluster."""
        print("[bold]Cluster[/bold] - Create")
        name = self.interactive_value("Cluster Name")
        payload = {
            "name": name
        }
        print("[bold]Cluster[/bold]")
        print("\t[bold]%s[/bold]\t%s" % ("Name", name))
        print("\n")
        self.interactive_bool("Create Cluster?")

        response = self.api.cluster_post(payload=payload, create=True)
        self.handle_error(response)

        print("[[bold green]SUCCESS[/bold green]] Cluster created successfully.")
        return True

    def delete(self) -> bool:
        """Delete a Cluster from Pignus."""
        if not self.args["options"]["id"]:
            print("ERROR: To delete a Cluster supply the Cluster ID.")
            exit(1)

        cluster_id = self.args["options"]["id"]
        response = self.api.cluster_get(cluster_id=cluster_id)
        self.handle_error(response)

        response_json = response.json()
        cluster = self.api.objects(response_json)
        self._display_cluster(cluster)
        self.interactive_bool("Delete Cluster?")

        response = self.api.cluster_delete(cluster_id=cluster_id)
        self.handle_error(response)

        print("[green bold][OK][/green bold] Cluster deleted successfully\n")

        return True

    def collection(self) -> bool:
        """Get all clusters."""
        response = self.api.clusters_get()
        self.handle_error(response)
        response_json = response.json()
        clusters = self.api.objects(response_json)

        print("[bold]Clusters[/bold] - %s" % len(clusters))
        for cluster in clusters:
            print("\t[bold]%s[/bold]" % cluster.name)
            print("\t\t[bold]ID[/bold]\t\t%s" % cluster.id)
            print("\t\t[bold]Slug Name[/bold]\t%s" % cluster.slug_name)
            print("\t\t[bold]Enabled[/bold]\t\t%s" % cluster.enabled)
            print("\t\t[bold]Last Check In:[/bold]\t%s" % client_misc.fmt_date(
                cluster.last_check_in))
        print("\n")

        return True

    def _display_cluster(self, cluster) -> bool:
        print("Cluster - [bold]%s[/bold]" % cluster.name)
        print("\t[bold]ID[/bold]\t\t%s" % cluster.id)
        print("\t[bold]Slug Name[/bold]\t%s" % cluster.slug_name)
        print("\t[bold]Enabled[/bold]\t\t%s" % cluster.enabled)
        print("\t[bold]Last Check In[/bold]\t%s" % client_misc.fmt_date(cluster.last_check_in))
        print("\n")
        return True

# End File: automox/pignus/src/pignus/cli/cli_cluster.py
