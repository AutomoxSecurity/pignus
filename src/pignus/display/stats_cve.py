# """Stats CVE
# """
# from pignus import misc


# class StatsCve:

#     def __init__(self, settings):
#         self.settings = settings
#         self.data = {
#             "first_seen": None,
#             "last_seen": None,
#             "clusters": {},
#             "num_images": 0,
#             "num_containers": 0,
#         }

#     def get(self, cve_number: str, images: list):
#         self.cve_number = cve_number
#         self.images = images
#         clusters = self.settings["config"]["cluster"]["supported"]
#         for image in images:
#             # Set general first seen
#             if not self.data["first_seen"]:
#                 self.data["first_seen"] = image.created_ts
#             if image.created_ts < self.data["first_seen"]:
#                 self.data["first_seen"] = image.created_ts

#             self.data["num_images"] += 1
#             for cluster in clusters:
#                 cluster_fields = misc.get_entity_cluster_fields(cluster)
#                 cluster_first_seen = getattr(image, cluster_fields["first_seen"])
#                 cluster_last_seen = getattr(image, cluster_fields["last_seen"])

#                 # Set general last seen
#                 if cluster_last_seen:
#                     if not self.data["last_seen"]:
#                         self.data["last_seen"] = cluster_last_seen

#                     if cluster_last_seen > self.data["last_seen"]:
#                         self.data["last_seen"] = cluster_last_seen

#                 if cluster_first_seen:
#                     # Set Cluster Specific first and last
#                     if cluster not in self.data["clusters"]:
#                         self.data["clusters"][cluster] = {
#                             "first_seen": None,
#                             "last_seen": None,
#                         }

#                     if not self.data["clusters"][cluster]["first_seen"]:
#                         self.data["clusters"][cluster][
#                             "first_seen"
#                         ] = cluster_first_seen

#                     if (
#                         cluster_first_seen < self.data["clusters"][cluster]["first_seen"]
#                     ):
#                         self.data["clusters"][cluster][
#                             "first_seen"
#                         ] = cluster_first_seen

#                     if not self.data["clusters"][cluster]["last_seen"]:
#                         self.data["clusters"][cluster]["last_seen"] = cluster_last_seen

#                     if cluster_last_seen > self.data["clusters"][cluster]["last_seen"]:
#                         cluster_last_seen = self.data["clusters"][cluster]["last_seen"]

#                 for container_digest, container in image.containers.items():
#                     if self.cve_number in container.scan_crowdstrike_cve_critical_names:
#                         self.data["num_containers"] += 1
#         return self.data


# # End File: automox/pignus/src/pignus/display/stats_cve.py
