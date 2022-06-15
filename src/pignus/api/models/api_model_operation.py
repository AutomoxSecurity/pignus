"""Api Model Operation
/role

Testing
    Unit Tests: automox/pignus/tests/unit/api/modles/api_model_operation.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.operation import Operation


class ApiModelOperation(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelOperation, self).__init__(event)
        self.model = Operation
        self.model_url = "/operation"
        self.perms = {
            "GET": "list-operations",
            "DELETE": "delete-operations"
        }

# End File: automox/pignus/src/pignus/api/models/api_model_operation.py
