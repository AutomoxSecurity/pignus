"""CLI Image

"""
from rich import print

from pignus.models.image import Image
from pignus.cli.cli_base import CliBase
from pignus.utils import client_misc


class CliImage(CliBase):

    def __init__(self, cli_parser):
        super(CliImage, self).__init__(cli_parser)
        self.route_options = {
            "get image": {
                "name": ["--name", "-n"],
                "id": ["--id", "-i"],
                "full": ["-full", "-f"]
            },
            "delete image": {
                "id": ["--id", "-i"],
            },
            "get images": {
                "name": ["--name", "-n"],
            },
        }

    def get(self):
        """Get information on a single Image from Pignus."""
        payload = {}
        if self.args["options"]["id"]:
            payload["id"] = self.args["options"]["id"]
        elif self.args["value"]:
            payload["name"] = self.args["value"]

        operations = [self.api.image_get]
        args = [{"payload": payload}]
        results = self.run_with_loader(operations, args)
        response = results[0]
        self.handle_error(response, payload)

        response_json = response.json()
        image = self.api.objects(response_json)
        self.get_clusters()
        self._display_image(image)

        print("\n")
        return image

    def delete(self) -> bool:
        """Delete an Image from Pignus."""
        if not self.args["options"]["id"]:
            print("ERROR: To delete an Image supply the Image ID.")
            exit(1)

        response = self.api.image_get(image_id=self.args["options"]["id"])
        self.handle_error(response)

        response_json = response.json()
        image = self.api.objects(response_json)
        self.get_clusters()
        self._display_image(image)

        self.interactive_bool("Delete Image?")

        response = self.api.image_delete(image_id=image.id)
        self.handle_error(response)

        print("[green bold][OK][/green bold] Image deleted successfully\n")

        return True

    def collection(self) -> bool:
        """Get information on all Images tracked by Pignus."""
        payload = self.collection_payload()

        response = self.api.images_get(payload)
        self.handle_error(response, payload)

        response_json = response.json()
        total_images = response_json["data"]["pages"]["total_objects"]
        per_page = response_json["data"]["pages"]["per_page"]
        page = response_json["data"]["pages"]["current_page"]
        last_page = response_json["data"]["pages"]["last_page"]
        images = self.api.objects(response_json)

        print("[bold underline]Images - %s[/bold underline] " % total_images)
        print("\tPage:\t\t%s" % page)
        print("\tLast Page:\t%s" % last_page)
        print("\tPer Page:\t%s" % per_page)
        print("\n")
        for image in images:
            print("[bold]%s[/bold]" % image.name)
            print("\tID:\t\t%s" % image.id)
            print("\tMaintained:\t%s" % image.maintained)
            print("\tCreated:\t%s" % client_misc.fmt_date(image.created_ts))
        print("\n")
        return True

    def search(self) -> bool:
        """Run a search for Images containing a given phrase against the Pignus Api.
        """
        payload = self.collection_payload()
        payload["name"] = self.args["value"]
        response = self.api.images_search_get(payload)
        self.handle_error(response, payload)

        # Unpack the Response
        response_json = response.json()
        images = self.api.objects(response_json)
        if response_json["data"]["pages"]:
            total_images = response_json["data"]["pages"]["total_objects"]
            per_page = response_json["data"]["pages"]["per_page"]
            page = response_json["data"]["pages"]["current_page"]
            last_page = response_json["data"]["pages"]["last_page"]
        else:
            total_images = len(images)
            per_page = None
            page = None
            last_page = None

        print("[bold underline]Images - %s[/bold underline] " % total_images)
        print("\tSearch:\t")
        print("\t\t%s:\t%s" % ("name", payload["name"]))
        if page:
            print("\tPage:\t\t%s" % page)
        if last_page:
            print("\tLast Page:\t%s" % last_page)
        if per_page:
            print("\tPer Page:\t%s" % per_page)
        print("\n")

        for image in images:
            print("[bold]%s[/bold]" % image.name)
            print("\tID:\t\t%s" % image.id)
            print("\tMaintained:\t%s" % image.maintained)
            print("\tCreated:\t%s" % client_misc.fmt_date(image.created_ts))
        print("\n")

        return True

    def _display_image(self, image: Image) -> bool:
        """Display the Image details
        """
        # Show the general Image data
        print("[bold]Image - %s[/bold]" % image.name)
        print("\t[bold]ID[/bold]\t\t\t%s" % image.id)
        print("\t[bold]Created[/bold]\t\t\t%s" % client_misc.fmt_date(image.created_ts))
        print("\t[bold]Maintained[/bold]\t\t%s" % image.maintained)
        print("\t[bold]Repositories[/bold]\t\t%s" % client_misc.fmt_list(image.repositories))

        # Show the Image Meta
        if image.meta:
            print("\t[bold]Meta[/bold]")
            for meta_key, meta in image.meta.items():
                if "ecr-fail" in meta["name"]:
                    print("\t\t[bold]Name[/bold]\t[red]%s[/red]" % meta["name"])
                else:
                    print("\t\t[bold]Name[/bold]\t%s" % meta["name"])
                    print("\t\t[bold]Value[/bold]\t%s" % meta["value"])

        print("\t[bold]Clusters[/bold] - %s" % len(image.clusters))
        for cluster_x, cluster in image.clusters.items():
            full_cluster = self.clusters[cluster["cluster_id"]]
            print("\t\t[bold]%s[/bold]" % full_cluster.name)
            print("\t\t\t[bold]Last Seen[/bold]\t%s" % client_misc.fmt_date(cluster["last_seen"]))
            print("\t\t\t[bold]First Seen[/bold]\t%s" % client_misc.fmt_date(cluster["first_seen"]))

        self._display_image_builds(image)

        return True

    def _display_image_builds(self, image: Image) -> bool:
        """Display an ImageBuild
        """
        limit_show = 10
        print("\t[bold]Builds[/bold] - %s" % len(image.builds))
        image_builds = image.builds
        if len(image_builds) >= limit_show:
            print("\tShowing only %s of %s, use --all to display more." % (
                limit_show, len(image_builds)))

        c = 0
        for build_digest, image_build in image_builds.items():
            c += 1
            if c == limit_show:
                break
            print("\t\t[bold]Tags[/bold]  %s" % client_misc.fmt_list(image_build.tags))
            print("\t\t\t[bold]ID[/bold]\t\t%s" % image_build.id)
            if "full" in self.args["options"] and self.args["options"]["full"]:
                print("\t\t\t[bold]Digest[/bold]\t\t%s" % client_misc.fmt_short_digest(
                    image_build.digest))
            else:
                print("\t\t\t[bold]Digest[/bold]\t\t%s" % image_build.digest)
            print("\t\t\t[bold]Maintained[/bold]\t%s" % image_build.maintained)
            print("\t\t\t[bold]Repository[/bold]\t\t%s" % image_build.repository)
            if image_build.pending_operation:
                print("\t\t\t[bold]Pending Op[/bold]\t%s" % image_build.pending_operation)
            elif image_build.sync_flag:
                print("\t\t\t[bold]Pending Op[/bold]\t%s" % "Sync")
            elif image_build.scan_flag:
                print("\t\t\t[bold]Pending Op[/bold]\t%s" % "Scan")

        return True

# End File: automox/pignus/src/pignus/cli/models/cli_image.py
