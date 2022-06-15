# """Display a cluster's details

# """
# import collections

# from rich import print
# from rich.console import Console
# from rich.table import Table

# from pignus.utils import date_utils
# from pignus.display.display_base import DisplayBase


# class DisplayCluster(DisplayBase):

#     def display(self, cluster_name: str, images: list, data: dict):
#         """Display cluster details, given a list of images."""
#         self.cluster_name = cluster_name
#         self.images = images
#         self.data = data
#         print("[bold]Cluster[/bold]:\t%s" % cluster_name)
#         print("[bold]Last Seen[/bold]:\t%s" % date_utils.human_date(data["last_check_in"]))
#         print("[bold]Num Images[/bold]:\t%s" % data["images"]["unique"])

#         print("[bold underline]CVE Details[/bold underline]")

#         if data["cves"]["critical"]["cve_numbers"]:
#             print("\t[bold]Critical[/bold]")
#             print("\t\tNum Cves:\t%s" % len(data["cves"]["critical"]["cve_numbers"]))
#             print("\t\tNum Images:\t%s (%s)%%" % (
#                 len(data["cves"]["critical"]["images"]),
#                 data["cves"]["critical"]["cve_percent"]
#             ))

#         if data["cves"]["high"]["cve_numbers"]:
#             print("\t[bold]High[/bold]")
#             print("\t\tNum Cves:\t%s" % len(data["cves"]["high"]["cve_numbers"]))
#             print("\t\tNum Images:\t%s (%s)%%" % (
#                 len(data["cves"]["high"]["images"]),
#                 data["cves"]["high"]["cve_percent"]
#             ))

#         if data["cves"]["medium"]["cve_numbers"]:
#             print("\t[bold]Medium[/bold]")
#             print("\t\tNum Cves:\t%s" % len(data["cves"]["medium"]["cve_numbers"]))
#             print("\t\tNum Images:\t%s (%s)%%" % (
#                 len(data["cves"]["medium"]["images"]),
#                 data["cves"]["medium"]["cve_percent"]
#             ))

#         if data["cves"]["low"]["cve_numbers"]:
#             print("\t[bold]Low[bold]")
#             print("\t\tNum Cves:\t%s" % len(data["cves"]["low"]["cve_numbers"]))
#             print("\t\tNum Images:\t%s (%s)%%" % (
#                 len(data["cves"]["low"]["images"]),
#                 data["cves"]["low"]["cve_percent"]
#             ))

#         self.display_images()

#         # self.display_images()
#         # self.show_image_stats()
#         # self.console.print(self.table)
#         # self.show_critical_images()

#     def display_images(self):
#         """Display the Images for the Cluster."""
#         display = "critical"
#         if self.args["options"]["show"] in ["c", "critical"]:
#             display = "critical"
#         elif self.args["options"]["show"] in ["a", "all"]:
#             display = "all"

#         self.set_image_repository_colors(self.images)
#         console = Console()
#         table = Table(show_header=True, header_style="bold yellow")
#         table.add_column("Image Name", width=60)
#         table.add_column("[red]Critical[/red]", width=8, justify="right")
#         table.add_column("[orange]High[/orange]", width=8, justify="right")
#         table.add_column("[yellow]Medium[/yellow]", width=8, justify="right")
#         table.add_column("Low", width=15, justify="right")

#         if display == "all":
#             self.display_images_all(table)
#         elif display == "critical":
#             self.display_images_critical(table)

#         console.print(table)
#         return True

#     def display_images_all(self, table):
#         """Display all Images """
#         print("\n[bold]All Images[/bold]")
#         severities = ["critical", "high", "medium", "low"]
#         for image in self.images:
#             row = [image.name]
#             for sev in severities:
#                 sev_value = getattr(image, "cve_%s_int" % sev)
#                 if not sev_value:
#                     sev_value = ""
#                 row.append(str(sev_value))
#             table.add_row(*row)
#         return True

#     def display_images_critical(self, table):
#         """Display Images with critical CVES"""
#         print("\n[bold]Images with Critical CVEs[/bold]")
#         severities = ["critical", "high", "medium", "low"]
#         for image in self.data["cves"]["critical"]["images"]:
#             row = [self.render_image(image.name)]
#             for sev in severities:
#                 sev_value = getattr(image, "cve_%s_int" % sev)
#                 if not sev_value:
#                     sev_value = ""
#                 if sev == "critical":
#                     sev_value = "[red]%s[/red]" % sev_value
#                 elif sev == "high":
#                     sev_value = "[orange]%s[/orange]" % sev_value
#                 elif sev == "medium":
#                     sev_value = "[yellow]%s[/yellow]" % sev_value
#                 row.append(str(sev_value))
#             table.add_row(*row)
#         return True

#     def _most_common_cve(self, images: list, limit: int = 5):
#         cves_group = {}
#         for image in images:
#             image_cves = getattr(image, "scan_crowdstrike_cve_critical_names")
#             if not image_cves:
#                 continue

#             for image_cve in image_cves:
#                 if image_cve not in cves_group:
#                     cves_group[image_cve] = 1
#                 else:
#                     cves_group[image_cve] += 1
#         cves_group = collections.OrderedDict(sorted(cves_group.items(), reverse=True))
#         cves_group = dict(list(cves_group.items())[:limit])
#         return cves_group


# # End File: automox/pignus/src/pignus/display/display_cluster.py
