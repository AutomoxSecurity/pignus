"""Api Collection Images
/images

Testing
    Unit Tests: automox/pignus/tests/unit/api/collections/test_api_collection_images.py

"""
from pignus.api.collections.api_collection_base import ApiCollectionBase
from pignus.collections.images import Images
from pignus.models.cluster import Cluster


class ApiCollectionImages(ApiCollectionBase):

    def __init__(self, event: dict):
        super(ApiCollectionImages, self).__init__(event)
        self.collection = Images()
        self.response["data"]["object_type"] = "image"
        self.collection_url = "/images"
        self.where_fields = ["name"]
        self.perms = {
            "GET": "list-images",
        }

    def class_routes(self) -> bool:
        """Handle the custom resources for a collection."""
        if not self.perm_check():
            self.response_403()
            return False

        if self.event["httpMethod"] == "GET":
            if self.resource == "/images/cluster":
                self.resource_handled = True
                self.get_images_cluster()
            elif self.resource == "/images/search":
                self.resource_handled = True
                self.get_images_search()
            elif self.resource == "/images/missing-auth":
                self.resource_handled = True
                self.get_images_missing_auth()

        return False

    def get_images_cluster(self) -> bool:
        """Get all Images within a given cluster in a paginated fashion."""
        cluster_slug_name = self.get_arg("cluster")
        if not cluster_slug_name:
            self.response_401("Missing required argument cluster")
            return False

        cluster = Cluster()
        if not cluster.get_by_field("slug_name", cluster_slug_name):
            self.response_404()
            return False

        page = int(self.get_arg("page", default=1))
        per_page = self.arg_per_page()

        collect_entities = Images().get_by_cluster_paginated(
            cluster_id=cluster.id,
            page=page,
            per_page=per_page)
        entity_models = collect_entities["objects"]
        for entity_model in entity_models:
            self.response["data"]["objects"].append(entity_model.json())
        self.response["data"]["pages"] = collect_entities["info"]
        return True

    def get_images_search(self) -> bool:
        """Run the search query against Pignus Images, creating a paginated list of results."""
        name = self.get_arg("name")
        search_qry = {
            "field": "name",
            "value": name
        }
        collect_entities = Images().get_like(search_qry)
        entity_models = collect_entities["objects"]
        for entity_model in entity_models:
            self.response["data"]["objects"].append(entity_model.json())
        self.response["data"]["pages"] = collect_entities["info"]
        return True

    def get_images_missing_auth(self) -> bool:
        """Get all Images that have been marked as missing authentication to sync an Image into the
        Pignus ECR.
        :unit-test: TestApiCollectionImages::test__get_images_missing_auth
        """
        aws_account = self.get_arg("account")
        if not aws_account:
            self.response_401("Missing account number.")
            return False

        collect_entities = Images().missing_auth(aws_account)
        entity_models = collect_entities["objects"]
        for entity_model in entity_models:
            self.response["data"]["objects"].append(entity_model.json(full=False))
        self.response["data"]["pages"] = collect_entities["info"]
        if not self.response["data"]["pages"]:
            self.response["data"]["pages"]["total_objects"] = len(entity_models)
        return True

# End File: automox/pignus/src/pignus/api/collections/api_collection_images.py
