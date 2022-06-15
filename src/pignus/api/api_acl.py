# """Api ACL
# /acl

# Testing
# Unit Tests at automox/pignus/tests/unit/api/test_api_acl.py

# """
# from pignus.api.api_base import ApiBase
# from pignus.models.image import Image
# from pignus.collections.clusters import Clusters
# from pignus.utils import date_utils
# from pignus.utils import log
# from pignus import image_add


# class ApiACL(ApiBase):

#     def __init__(self, event: dict):
#         super(ApiACL, self).__init__(event)
#         self.response["status_code"] = 200

#     def handle(self) -> dict:
#         """Route requests for /acl"""
#         if self.event["httpMethod"] == "POST":
#             self.get()
#         else:
#             self.response_404()

#         return self.response

#     def get(self):
#         """Get the built out ACL relationships. """
#         return True


# # End File: automox/pignus/src/pignus/api/api_acl.py
