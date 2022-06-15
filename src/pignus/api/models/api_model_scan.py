"""Api Model Scan
/scan

Testing
    Unit Tests: automox/pignus/tests/unit/api/modles/test_api_model_scan.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.scan import Scan


class ApiModelScan(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelScan, self).__init__(event)
        self.model = Scan
        self.entity = None
        self.post_create = False
        self.delete_destroy = False
        self.model_url = "/scan"
        self.perms = {
            "GET": "list-scans",
        }

# End File: automox/pignus/src/pignus/api/api_model_scan.py
