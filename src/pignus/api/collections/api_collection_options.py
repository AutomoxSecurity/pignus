"""Api Collection Options
Handles /options

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.options import Options


class ApiCollectionOptions(ApiCollectionBase):
    def __init__(self, event: dict):
        super(ApiCollectionOptions, self).__init__(event)
        self.collection = Options()
        self.response["data"]["object_type"] = "option"
        self.collection_url = "/options"

    def get(self):
        """GET /entities/ collections in a paginated fashion. For options we'll remove "pages" from
        the api return since we return all results in one page.
        """
        self.response["data"]["objects"] = {}
        options = Options().load_options()

        for option_name, option in options.items():
            self.response["data"]["objects"][option_name] = option.json()

        self.response["data"].pop("pages")
        return True

# End File: automox/pignus/src/pignus/api/api_collection_options.py
