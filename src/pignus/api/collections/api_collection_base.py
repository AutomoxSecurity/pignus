"""Api Collection Base

Testing
    Unit Tests: automox/pignus/tests/unit/api/test_api_collection_base.py
    7/7 Unit-Tested
    100% Test Coverage!

"""
from pignus.api.api_base import ApiBase


class ApiCollectionBase(ApiBase):

    def __init__(self, event: dict):
        """
        Class Vars
            - collection: The model's collection class

        :unit-test: TestApiCollectionBase::test____init__
        """
        super(ApiCollectionBase, self).__init__(event)
        self.collection = None
        self.uri_subject_field = None
        self.resource_handled = False
        self.collection_url = None
        self.where_fields = []
        self.order_by = {
            "field": "created_ts",
            "op": "DESC"
        }
        self.per_page_default = 20
        self.per_page_max = 50
        self.response["data"] = {}
        self.response["data"]["object_type"] = ""
        self.response["data"]["pages"] = {}
        self.response["data"]["objects"] = []

    def handle(self) -> dict:
        """Routes requests for a model to the method which will serve them.
        :unit-test: TestApiCollectionBase::test__handle
        """
        if not self.parse_success:
            return self.response

        self.resource = self.event["path"]

        # Use class specific routes if they exist
        self.class_routes()

        # If the boiler plate routes don't match, check the model's specific routes.
        if not self.resource_handled:
            if self.event["httpMethod"] == "GET" and self.event["path"] == self.collection_url:
                if self.resource == self.collection_url:
                    self.resource_handled = True
                    self.get()

        # If we still haven't matched a route, return a 404.
        if not self.resource_handled:
            self.response_404()

        return self.response

    def class_routes(self):
        """
        :unit-test: TestApiCollectionBase::test__class_routes
        """
        return False

    def get(self) -> bool:
        """GET /entities/ collections in a paginated fashion.
        :unit-test: TestApiCollectionBase::test__get
        """
        # Check permission
        if not self.perm_check():
            self.response_403()
            return False

        self.response["data"]["pages"] = {}
        page = int(self.get_arg("page", default=1))
        per_page = self.arg_per_page()
        order = self._order()
        where = self._where()
        collect_entities = self.collection.get_paginated(
            page=page,
            per_page=per_page,
            where_and=where,
            order_by=order)
        entity_models = collect_entities["objects"]
        for entity_model in entity_models:
            self.response["data"]["objects"].append(entity_model.json())
        self.response["data"]["pages"] = collect_entities["info"]

        return True

    def arg_per_page(self) -> int:
        """Get the argument "per_page" for paginatated returns. Checvk to see if the "per_page"
        argument was submitted in the request. If it was set, it as the value, checking that it is
        under the classes specifified max.
        :unit-test: TestApiCollectionBase::test___arg_per_page()
        """
        per_page = self.get_arg("per_page")

        if not per_page:
            return self.per_page_default

        per_page = int(per_page)

        if per_page > self.per_page_max:
            per_page = self.per_page_max

        return per_page

    def _order(self) -> dict:
        """Get the "order" clause for collection request.
        :unit-test: TestApiCollectionBase::test___order()
        """
        user_order_by = self.get_arg("order_by")
        if not user_order_by and self.order_by:
            order = self.order_by
            return order

        order_field = self.get_arg("order_by", default="created_ts")
        order_op = self.get_arg("order_op", default="DESC")

        order = {
            "field": order_field,
            "op": order_op,
        }
        return order

    def _where(self) -> list:
        """Get the "where" clause for a collection request. The collection object must specify the
        fields allowed to be used in a where query in the self.where_fields var. Currently this
        only allows multiples to be joined to gether as "AND".
        :unit-test: TestApiCollectionBase::test___where()
        """
        if not self.where_fields:
            return []
        where_query = []
        for field in self.where_fields:
            where_value = self.get_arg(field)
            if not where_value:
                continue
            where_op = {
                "field": field,
                "value": where_value
            }
            where_query.append(where_op)
        return where_query

# End File: automox/pignus/src/pignus/api/api_collection_base.py
