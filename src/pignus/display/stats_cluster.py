# """Stats Cluster
# Generate stats based on the Images running in the Cluster.

# """
# from pignus.utils import mathy


# class StatsCluster:

#     def __init__(self):
#         self.data = {
#             "unique_images": 0,
#             "last_check_in": None,
#             "images": {
#                 "unique": 0,
#                 "auth_failures": 0,
#             },
#             "security": {},
#         }

#     def get(self, cluster: str, images: list):
#         self.images = images
#         self.data["images"]["unique"] = len(images)
#         self.data["last_check_in"] = None

#         # Set the basic Cluster Stats
#         for image in images:
#             # Set Cluster Seen
#             if not self.data["last_check_in"]:
#                 self.data["last_check_in"] = image.clusters[cluster]["last_seen"]
#             if image.clusters[cluster]["last_seen"] > self.data["last_check_in"]:
#                 self.data["last_check_in"] = image.clusters[cluster]["last_seen"]

#             # @todo: This needs to be redone
#             # if image.repository_auth_missing:
#             #     self.data["images"]["auth_failures"] += 1

#         self.images = mathy.order_images_by_cves(self.images)
#         self.data["cves"] = self.get_security()

#         return self.data

#     def get_security(self) -> dict:
#         """Get CVE details from Images."""
#         data = {
#             "critical": {
#                 "cve_numbers": [],
#                 "images": [],
#             },
#             "high": {
#                 "cve_numbers": [],
#                 "images": [],
#             },
#             "medium": {
#                 "cve_numbers": [],
#                 "images": [],
#             },
#             "low": {
#                 "cve_numbers": [],
#                 "images": [],
#             },
#         }
#         severities = ["critical", "high", "medium", "low"]
#         for image in self.images:
#             for sev in severities:
#                 cves = getattr(image, "cve_%s_nums" % sev)
#                 if not cves:
#                     continue

#                 data[sev]["cve_numbers"] = data[sev]["cve_numbers"] + cves
#                 data[sev]["images"].append(image)
#                 data[sev]["cve_percent"] = mathy.percentage(
#                     len(data[sev]["images"]),
#                     len(self.images), round_int=0)

#         return data


# # End File: automox/pignus/src/display/stats_cluster.py
