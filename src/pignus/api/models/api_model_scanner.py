"""Api Model Scanner
/scanner

Testing
    Unit Tests: automox/pignus/tests/unit/api/models/test_api_model_cluster.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.scanner import Scanner


class ApiModelScanner(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelScanner, self).__init__(event)
        self.model = Scanner
        self.post_create = True
        self.delete_destroy = True
        self.model_url = "/scanner"

# End File: automox/pignus/src/pignus/api/models/api_model_cluster.py
