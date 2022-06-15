"""Api Model Option
/option

Testing
    Unit Tests: automox/pignus/tests/unit/api/models/test_api_model_option.py
    1/1 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.option import Option


class ApiModelOption(ApiModelBase):

    def __init__(self, event: dict):
        """
        :unit-test: TestApiModelOption::test____init__
        """
        super(ApiModelOption, self).__init__(event)
        self.model = Option
        self.uri_subject_field = "name"
        self.post_create = False
        self.modifiable_fields = ["value"]
        self.model_url = "/option"
        self.perms = {
            "GET": "list-options",
            "POST": "post-options",
        }

    def delete(self):
        """Don't allow an Option to be deleted.
        :unit-test: TestApiModelOption::test__delete
        """
        self.response["status_code"] = 401
        self.response["message"] = "Deleting Options is forbidden."
        return False

# End File: automox/pignus/src/pignus/api/models/api_model_option.py
