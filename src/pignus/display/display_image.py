# """Display Image
# Pretty print an image and its data to the console

# """
# from rich import print
# from rich.columns import Columns
# from rich.console import Console
# from rich.padding import Padding

# from pignus.models.image import Image
# from pignus.models.container import Container
# from pignus.display.display_base import DisplayBase

# from pignus import misc


# class DisplayImage(DisplayBase):

#     def display(self, image: Image, data: dict):
#         """Display Image details."""
#         self.last_color = None
#         self.image = image
#         self.image_data = data
#         self.display_general()
#         self.display_pignus()
#         self.display_clusters()
#         # self.display_security()
#         self.display_containers()

#     def display_general(self):
#         """Display Image's general details."""
#         print("[bold]Name[/bold]:\t\t%s" % self.image.name)
#         print("[bold]Repositories[/bold]:\t%s" % (self.image.repositories))
#         print("[bold]Containers[/bold]:\t%s" % (len(self.image.containers)))

#     def display_pignus(self):
#         """Display Image's details related to the Pignus process."""
#         print("%s" % self.bold("Pignus"))
#         print("\t%s:\t\t%s" % (self.bold("ID"), self.image.id))
#         print("\t%s:\t%s" % (self.bold("Maintained"), self.image.maintained))
#         print("\t%s:\t%s" % (self.bold("First Seen"), self.render_date(self.image.created_ts)))
#         # Todo Last Seen
#         # print("\t%s:\t%s" % (self.bold("Last Seen"), self.render_date(self.image.last_seen)))
#         # self.render_date(self.image_data["cluster"]["last_seen"]),
#         print("\t%s:\t%s" % (self.bold("Updated"), self.render_date(self.image.updated_ts)))

#     def display_clusters(self) -> bool:
#         """Display the Image's cluster details """
#         print("[bold]Clusters[/bold]")

#         if not self.image.clusters:
#             print("\t\t[bold]Not in any clusters[/bold]")
#             return True

#         for cluster_name, cluster in self.image.clusters.items():
#             print("\t[underline bold]%s[/underline bold]" % cluster_name.title())
#             if cluster["last_seen"]:
#                 print("\t\t[bold]Currently Present[/bold]:\t%s" % cluster["present"])
#                 print("\t\t[bold]First Seen[/bold]:\t\t%s" % self.render_date(cluster["first_seen"]))
#                 print("\t\t[bold]Last Seen[/bold]:\t\t%s" % self.render_date(cluster["last_seen"]))

#         return True

#     def display_containers(self):
#         number_maintained = 0
#         for container_digest, container in self.image.containers.items():
#             if container.maintained:
#                 number_maintained += 1
#         self.add_row("[bold]Containers[/bold]")
#         self.add_row("Total", self.rf(len(self.image.containers)))
#         self.add_row("Maintained", self.rf(number_maintained))
#         container_mode = "verbose"
#         if len(self.image.containers) > 5:
#             container_mode = "slim"
#         elif len(self.image.containers) > 20:
#             container_mode = "only-live"

#         if container_mode == "verbose":
#             self._containers_verbose()
#         elif container_mode == "only-live":
#             self.containers_only_live()
#         else:
#             self._containers_slim()

#     def display_security(self):
#         """Display Image security details."""
#         print("%s" % self.bold("CVEs"))
#         self._handle_cve_level("critical")
#         self._handle_cve_level("high")
#         self._handle_cve_level("medium")
#         self._handle_cve_level("low")

#     def _handle_cve_level(self, level: str) -> bool:
#         """Display the Image's CVE's for a given criticality."""
#         cve_int = getattr(self.image, "cve_%s_int" % level)
#         cve_nums = getattr(self.image, "cve_%s_nums" % level)
#         if not cve_nums:
#             return True
#         if cve_int:
#             cve_nums = getattr(self.image, "cve_%s_nums" % level)
#         else:
#             cve_int = 0

#         if len(level) > 6:
#             tabs = "\t"
#         else:
#             tabs = "\t\t"
#         console = Console(width=100)
#         cves_text = Padding(
#             Columns(
#                 [
#                     "[bold]%s[/bold]" % level.title(),
#                     "%s(%s)" % (tabs, cve_int)
#                 ]
#             ),
#             (0, 0, 0, 8))
#         console.print(cves_text)
#         console = Console(width=100)
#         cves_text = Padding(Columns(cve_nums), (0, 0, 0, 16))
#         console.print(cves_text)

#         return True

#     def _containers_slim(self):
#         if not self.image.containers:
#             return

#     def _containers_verbose(self):
#         data = {
#             "total": len(self.image.containers),
#             "maintained": 0,
#         }

#         for container_dig, container in self.image.containers.items():
#             if container.maintained:
#                 data["maintained"] += 1

#         self.add_row("Maintained", self.rf(data["maintained"]), "", "")
#         if self.image.containers:
#             self.add_row(
#                 "",
#                 "[bold][underline]Digest[/underline][/bold]",
#                 "[bold][underline]Tag[/underline][/bold]",
#                 "",
#             )
#         for container_digest, container in self.image.containers.items():
#             self._container_verbose(container)

#     def _container_verbose(self, container: Container):
#         """Display details on a self.images container."""
#         color = self.random_color(self.last_color)
#         self.last_color = color
#         # self.add_row(
#         #     "",
#         #     self.rf(container.short_id(), color=color, bold=True),
#         #     self.rf(container.tag, color=color, bold=True),
#         #     "",
#         # )

#         if not container.maintained:
#             msg = "[red]False[/red]"
#         elif container.maintained:
#             msg = "[green]True[/green]"
#         self.add_row("", "", "Maintained", msg)
#         self.add_row("", "", "Last", self.render_date(container.sync_last_ts, False))

#         # self._container_security(container)
#         # self._container_cluster(container)

#     def _container_security(self, container: Container):
#         # Handle Security
#         self.add_row("", "", "[bold][underline]Security[/underline][/bold]", "")
#         if container.scan_build_id:
#             self.add_row("", "", "[green bold]SCAN IN PROGRESS[/green bold]", "")

#         self.add_row(
#             "", "", "Last Scan", self.render_date(container.scan_last_ts)
#         )

#         # self._container_cve("critical", container)
#         # self._container_cve("high", container)

#     def _container_cve(self, level, container: Container):
#         value = container.cve_critical_int
#         if not value or value == 0:
#             return False
#         self.add_row("", "", "%s" % level.title(), value)

#     def _container_cluster(self, container: Container):
#         """Display cluster info for a single Container."""
#         # If there's only 1 Container for the Image this info is redundant.
#         if len(self.image.containers) == 1:
#             return
#         self.add_row("", "", self.rf("Clusters", bold=True, underline=True), "")
#         for cluster in self.settings["config"]["cluster"]["supported"]:
#             cluster_fields = misc.get_entity_cluster_fields(cluster)
#             cluster_first_seen = getattr(container, cluster_fields["first_seen"])
#             cluster_present = getattr(container, cluster_fields["present"])
#             if not cluster_first_seen:
#                 continue

#             self.add_row(
#                 "",
#                 "",
#                 self.rf(cluster.upper(), bold=True),
#             )

#             if cluster_present:
#                 self.add_row(
#                     "",
#                     "",
#                     self.rf("Live Now"),
#                     self.rf("True", color="green", bold=True),
#                 )
#             self.add_row(
#                 "", "", self.rf("First Seen"), self.render_date(cluster_first_seen)
#             )

# # End File: automox/pignus/src/pignus/display_image.py
