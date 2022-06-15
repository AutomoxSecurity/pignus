# """Stats Image
# Collect stats for a single Image
# """
# from pignus.models.image import Image


# class StatsImage:

#     def __init__(self):
#         self.image = None
#         self.data = {
#             "cluster": {
#                 "last_seen": None
#             }
#         }

#     def get(self, image: Image) -> dict:
#         """Get stats for a single Image."""
#         self.image = image

#         # Get cluster stats
#         self._get_cluster_last_seen()
#         return self.data

#     def _get_cluster_last_seen(self) -> True:
#         """Get the Image's last seen date from the cluster_data."""
#         for cluster_name, cluster in self.image.clusters.items():
#             if not cluster["last_seen"]:
#                 continue

#             if not self.data["cluster"]["last_seen"]:
#                 self.data["cluster"]["last_seen"] = cluster["last_seen"]

#             if cluster["last_seen"] > self.data["cluster"]["last_seen"]:
#                 self.data["cluster"]["last_seen"] = cluster["last_seen"]

#         return True

# # End File: automox/pignus/src/display/stats_image.py
