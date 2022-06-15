# """Display Images
# Pretty print an collection of images.

# """
# from rich.table import Table
# from rich import print

# from pignus.display.display_base import DisplayBase
# from pignus.models.image import Image


# class DisplayImages(DisplayBase):

#     def display(self, images, title=None):
#         self.clusters = self.settings["server"]["cluster"]["supported"]
#         self.images = images
#         self.title = title

#         if self.title:
#             self.title = "[bold]%s[/bold]"
#         else:
#             self.title = "[bold]Images[/bold]"
#         self.title += "\tTotal: %s " % len(self.images)
#         self.field_display = 1
#         self.fields = []
#         self.set_display_scale()
#         self._get_cell_width()
#         self.set_image_repository_colors(self.images)

#         self.table = Table(header_style="bold magenta")
#         self.table.add_column("Title", width=self.column_name_len)
#         self.table.add_column("", width=25)
#         self.table.add_column("", width=37)

#         if self.args["limit"] != 0:
#             if len(self.images) > self.args["limit"]:
#                 images = self.images[: self.args["limit"]]
#                 self.images = images

#         if self.field_display == 1:
#             self.draw_images_slim()
#         else:
#             for image in self.images:
#                 self.draw_image(image)
#             self.console.print(self.table)

#     def _get_cell_width(self):
#         longest_title = 0
#         for image in self.images:
#             if len(image.name) > longest_title:
#                 longest_title = len(image.name)
#         self.column_name_len = longest_title + 2
#         return True

#     def draw_images_slim(self):
#         print("[bold underline]Images[/bold underline]")
#         for image in self.images:
#             print("\t%s" % self.render_image(image.name))

#     def draw_image(self, image: Image):
#         """Draw a single image."""
#         color = self.random_color(self.last_color)
#         self.last_color = color
#         self.add_row(self.rf(image.name, color=color, bold=True))
#         # image_cluster_last = image.last_seen(self.clusters)
#         if self.show(5):
#             self.add_row(self.rf("General", bold=True, underline=True), pad=1)
#         if self.show(5, "maintained"):
#             self.add_row("Maintained", image.maintained, pad=1)

#         self.add_row("First Seen", self.render_date(image.created_ts), pad=1)
#         # if image_cluster_last["last_seen"]:
#         #     self.add_row(
#         #         "Last Seen",
#         #         self.rf(
#         #             self.render_date_live(image_cluster_last["last_seen"]),
#         #             color="green",
#         #             bold=True,
#         #         ),
#         #         pad=1,
#         #     )
#         # else:
#         #     self.add_row("Last Seen", "Never seen in cluster", pad=1)

#         if self.show(5, "updated_ts"):
#             self.add_row("Updated", self.render_date(image.updated_ts), pad=1)

#         if self.show(5, "containers"):
#             self.add_row("", "Containers", len(image.containers))

#         # self.draw_image_security(image)

#         # self.draw_image_cluster(image)

#         return True

#     def draw_image_security(self, image: Image):
#         """Display Image security details."""
#         cves = image.get_cves()
#         security_check = False
#         if len(cves["cve_critical_names"]) == 0:
#             security_check = True

#         if self.show(2) or security_check:
#             msg = ""
#             if security_check:
#                 msg = "[green bold][PASS][/green bold]"
#             else:
#                 msg = "[red bold][FAIL][/red bold]"
#             self.add_row(self.rf("Security", bold=True, underline=True), msg, pad=1)

#         if not security_check:
#             self.add_row(
#                 "\tCritical",
#                 self.rf(len(cves["cve_critical_names"]), bold=True, color="red"),
#                 pad=1,
#             )
#             if self.field_display >= 10:
#                 if len(cves["cve_critical_names"]) > 0:
#                     self.add_row(self.rf(cves["cve_critical_names"]), pad=2)

#     def draw_image_cluster(self, image: Image):
#         image_cluster_last = image.last_seen(self.clusters)
#         num_clusters = 0
#         if self.show(3):
#             self.add_row(self.rf("Clusters", bold=True, underline=True), pad=1)

#         for cluster_name in self.clusters:
#             cluster_info = image.get_cluster(cluster_name)
#             if not cluster_info["first_seen"]:
#                 continue
#             last_seen = self.render_date_live(image_cluster_last["last_seen"])
#             if self.show(5):
#                 self.add_row(
#                     "\t[bold]%s[/bold]" % cluster_name.upper(), last_seen, pad=1
#                 )
#             elif self.show(1):
#                 num_clusters += 1


# # End File: automox/pignus/src/pignus/display/display_images.py
