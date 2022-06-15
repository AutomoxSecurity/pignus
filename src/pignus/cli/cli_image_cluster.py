"""CLI ImageCluster
Handles all interactions with the Pignus API for ImageCluster requests.

"""
from rich import print

from pignus.cli.cli_base import CliBase


class CliImageCluster(CliBase):

    def collection(self) -> bool:
        """Get information on all ImageClusters tracked by Pignus."""
        payload = {}
        if self.args["options"]["page"]:
            payload["page"] = self.args["options"]["page"]
        if self.args["options"]["limit"]:
            payload["per_page"] = self.args["options"]["limit"]

        response = self.api.image_clusters_get(payload)

        if response.status_code != 200:
            print("ERORR: %s Could not fetch /image-clusters from Pignus" % response.status_code)
            if self.args["options"]["debug"]:
                print(response.text)
            exit(1)
        response_json = response.json()
        total = response_json["data"]["pages"]["total_objects"]
        per_page = response_json["data"]["pages"]["per_page"]
        page = response_json["data"]["pages"]["current_page"]
        last_page = response_json["data"]["pages"]["last_page"]
        image_clusters = self.api.objects(response_json)

        print("[bold]Image-Clusters[/bold] - %s" % total)
        print("\tPage:\t\t%s" % page)
        print("\tLast Page:\t%s" % last_page)
        print("\tPer Page:\t%s" % per_page)
        print("\n")
        for image_cluster in image_clusters:
            print("[bold]%s[/bold]" % image_cluster.name)
            print("\tID:\t%s" % image_cluster.id)

        return True


# End File: automox/pignus/src/pignus/cli/cli_image_cluster.py
