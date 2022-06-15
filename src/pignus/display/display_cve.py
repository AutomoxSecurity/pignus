# """Display a CVE.

# """
# from pignus.display.display_base import DisplayBase
# from pignus.display.display_images import DisplayImages


# class DisplayCve(DisplayBase):

#     def display(self, cve_number: str, images: list, data: dict):
#         self.cve_number = cve_number
#         self.images = images
#         self.data = data
#         self.table.add_column("Title", width=15)
#         self.table.add_column("", width=20)
#         self.table.add_column("", width=30)
#         self.table.add_row("CVE", self.render_header(self.cve_number))
#         self.add_row("Severity", "CRITICAL")
#         self.add_row("First Observed", self.render_date(self.data["first_seen"]))
#         self.add_row("Last Observed", self.render_date(self.data["last_seen"]))
#         self.add_row("Clusters", len(self.data["clusters"]))

#         for cluster_name, cluster_details in self.data["clusters"].items():
#             if cluster_name == "test":
#                 continue
#             self.add_row(cluster_name.upper(), "")
#             self.add_row(
#                 "", "First Seen", self.render_date(cluster_details["first_seen"])
#             )
#             self.add_row(
#                 "", "Last Seen", self.render_date(cluster_details["last_seen"])
#             )

#         self.add_row("Images", len(self.images))
#         self.add_row("Containers", self.data["num_containers"])

#         self.console.print(self.table)

#         self.show_cve_images()

#     def show_cve_images(self):
#         DisplayImages(self.settings, self.args).display(
#             self.images, "Images with %s" % self.cve_number)

# # End File: automox/pignus/src/pignus/display/display_cve.py
