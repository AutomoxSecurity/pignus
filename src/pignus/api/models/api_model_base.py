"""Api Model Base
This class serves as the base for all Pignus api models. All standard Pignus models that are exposed
via the api extended this class.

Testing
    Unit
        File       automox/pignus/tests/unit/api/models/test_api_model_base.py
        Methods    12/16 methods currently unit tested.

"""
from pignus.api.api_base import ApiBase
from pignus.utils import xlate
from pignus.utils import log


class ApiModelBase(ApiBase):

    def __init__(self, event: dict):
        """Setup for a generic ApiModel. This extends ApiBase, to utilize the core features of all
        api interactions.

        class vars
            self.model          Set to an instance of the model the api is representing
            self.entity         Should be left None, this will be used as the instance of the model for
                                the class to operate on.
            self.post_create    Bool flag
            @todo: Finish documenting
        :unit-test: TestApiModelBase::test____init__
        """
        super(ApiModelBase, self).__init__(event)
        self.model = None
        self.entity = None
        self.uri_subject_field = None
        self.resource_handled = False
        self.resource = None
        self.post_create = False
        self.model_url = None
        self.modifiable_fields = []
        self.createable_fields = []
        self.model_required_fields = []

    def handle(self) -> dict:
        """Routes requests for a model to the method which will serve them."""
        if not self.parse_success:
            return self.response
        self.resource = self.event["path"]

        if self.resource == self.model_url:
            if self.event["httpMethod"] == "GET":
                self.resource_handled = True
                self.get()
            elif self.event["httpMethod"] == "POST":
                self.resource_handled = True
                self.post()
            elif self.event["httpMethod"] == "DELETE":
                self.resource_handled = True
                self.delete()

        # If the boiler plate routes don't match, check the model's specific routes.
        if not self.resource_handled:
            self.class_routes()

        # If we still haven't matched a route, return a 404.
        if not self.resource_handled:
            self.response_404()

        return self.response

    def class_routes(self) -> bool:
        """Routes requests specific to a given Model object.
        :unit-test: TestApiModelBase::test__class_routes()
        """
        return True

    def load_model_default(self) -> bool:
        """Method for child classes to override to define how a model should be loaded by default.
        :unit-test: TestApiModelBase::test__load_model_default()
        """
        return True

    def find_entity(self) -> bool:
        """Find an entity which is the subject of the primary API request. Set the result to the
        class var self.entity with the model object or None depending on it's existance in the
        Pignus database.
        :unit-test: TestApiModelBase::test__find_entity()
        """
        log.info("Running find_entity: %s" % self.resource)
        log.info("query_params: %s" % self.query_params)
        log.info("body: %s" % self.post_body)
        entity_id = self.get_arg("id")
        entity_name = self.get_arg("name")

        log.info("entity_id: %s" % entity_id)
        log.info("entity_name: %s" % entity_name)
        self.entity = self.model()
        if entity_id:
            found = self.entity.get_by_id(entity_id)
        elif entity_name:
            found = self.entity.get_by_name(entity_name)
        else:
            log.warning(
                "Cannot find an image with the given criteria",
                query_params=self.query_params,
                post_body=self.post_body,
            )
            return False
        if not found:
            return False
        return True

    def get(self) -> dict:
        """Handle a GET request on /{model}, retrieving a generic model the data if it exists.
        :unit-test: TestApiModelBase::get
        """
        if not self.perm_check():
            self.response_403()
            return False

        # If the entity was not found
        if not self.find_entity():
            log.debug("Did not find model, 404")
            self.response_404()
            return False

        # Entity was found, run the default load out for the model
        self.load_model_default()
        self.response["data"]["object_type"] = self.model.model_name
        self.response["data"]["object"] = self.entity.json()
        return True

    def post(self) -> bool:
        """Handle a POST request on a /{model}, updating or creating an model via the API.
        :unit-test: TestApiModelBase::test__post
        """
        log.info("API MODEL BASE SERVING METHOD: POST")

        # Check permission
        if not self.perm_check():
            self.response_403()
            return False

        # If the request wants to create the model
        create = self.get_arg("create")
        if create:
            if not self._post_create():
                return False
            self.response["message"] = "%s created successfully" % self.entity

        # If the request wants to modify the model
        else:
            if not self._post_edit():
                return False
            self.response["message"] = "%s updated successfully" % self.entity

        self.response["status_code"] = 201
        self.response["status"] = "Success"
        self._post_apply_fields()
        self.entity.save()
        self.response["data"]["object_type"] = self.model.model_name
        self.response["data"]["object"] = self.entity.json()
        log.debug("Model updated successfully: %s" % self.entity)
        return True

    def delete(self) -> bool:
        """Method for deleting a model via an approved interface.
        :unit-test: TestApiModelBase.test__delete
        """
        # Check permission
        if not self.perm_check():
            self.response_403()
            return False

        self.response["data"]["object_type"] = self.model.model_name
        log.info("API MODEL BASE SERVING METHOD: delete")
        self.response["status_code"] = 201
        found = self.find_entity()

        # If we didn't find the model to delete.
        if not found:
            self.response_404()
            return False

        # Delete the model and it's children.
        delete_success = self.entity.delete()
        if not delete_success:
            log.warning("Delete did not succeed", entity=self.entity)
            self.response["status_code"] = 503
            self.response["message"] = "Error deleting entity: %s" % self.entity
            return False

        # Move this to the Image Api
        # Delete the ECR repository if request asks.
        # delete_ecr = self.get_arg("delete_ecr")
        # if delete_ecr:
        #     response = aws.delete_repository(image)
        #     if response:
        #         log.debug(
        #             "Image and ecr repository deleted successfully",
        #             image=image,
        #             stage="delete-image",
        #         )
        #     else:
        #         log.warning(
        #             "Error deleting repository: %s" % image.name,
        #             image=image,
        #             stage="delete-image",
        #         )

        self.response["data"]["object"] = self.entity.json()
        self.response["message"] = "%s deleted successfully." % self.model.model_name.title()
        return True

    def _post_create(self) -> bool:
        """Create a model instance, but first check,
            - The model api allows creationion, via self.post_create
            - The model allows the submitted fields for creation
            - The request has the mininum required fields to create a model
            - The model doesn't already exists
        """
        if not self._post_create_validate_action():
            return False

        if not self._post_create_validate_create_fields():
            return False

        if not self._post_create_validate_create_required_fields():
            return False

        #   @todo: The model doesn't already exists

        self.entity = self.model()

        return True

    def _post_create_validate_action(self) -> bool:
        """Check that api model allows creates though the self.post_create argument.
        :unit-test: TestApiModelBase::test___post_create_validate_action
        """
        if not self.post_create:
            error_msg = "Create is not allowed for %s" % self.model
            self.response_403(error_msg)
            return False
        return True

    def _post_create_validate_create_fields(self) -> bool:
        """Check that the submitted fields are allowed when creating the model.
        :unit-test: TestApiModelBase::test___post_create_validate_create_fields
        """
        params = self.post_body
        for field, value in params.items():
            if field == "create":
                continue
            if field not in self.createable_fields:
                error_msg = "Field: %s is not allowed as a field for creating %s models" % (
                    field, self.model)
                self.response_401(error_msg)
                return False
        return True

    def _post_create_validate_create_required_fields(self) -> bool:
        """Check that the submitted fields for creating a model cover the required minimums.
        :unit-test: TestApiModelBase::test___post_create_validate_create_required_fields
        """
        params = self.post_body
        all_required = True
        if not self.model_required_fields:
            log.warning("Model %s has no required fields." % self.model)
        for field_name in self.model_required_fields:
            if field_name not in params:
                all_required = False
        if not all_required:
            self.response_401("Create model %s requires fields that are missing." % self.model)
            return False
        return True

    def _post_cannot_create_401_exists(self, model) -> bool:
        """Response for POST request asking to create an entity that already exists.
        :unit-test: TestApiModelBase::test___post_cannot_create_401_exists
        """
        self.response["status"] = "Error"
        self.response["status_code"] = 401
        self.response["message"] = "Cannot create entity, it already exists."
        # self.response["message"] = \
        #     "Cannot create %s it already exists." % self.model.model_name.title()
        self.response["data"]["object_type"] = model.model_name
        self.response["data"]["object"] = model.json()
        return False

    def _post_edit(self) -> bool:
        """Edit a model instance, but first check,
            - The model api allows modification of the requested fields.
            - The entity exists.
        :unit-test: TestApiModelBase::test___post_edit_validate_modify_fields
        """
        if not self._post_edit_validate_modify_fields():
            return False

        found = self.find_entity()
        if not found:
            self.response_404()
            return False

        return True

    def _post_edit_validate_modify_fields(self) -> bool:
        """Check that the submitted fields are allowed when modifying the model.
        :unit-test: TestApiModelBase::test___post_edit_validate_modify_fields
        """
        params = self.post_body
        for field, value in params.items():
            if field == "id":
                continue
            if field not in self.modifiable_fields:
                error_msg = "Field: %s is not allowed for modification for %s models" % (
                    field, self.model)
                self.response_401(error_msg)
                return False
        return True

    def _post_apply_fields(self) -> True:
        """Apply the fields submitted through the api to the model object as it currently exists.
        :unit-test: TestApiModelBase::test___post_apply_fields
        """
        params = self.post_body
        skip_fields = ["id", "create"]
        for field_name, field_value in params.items():
            if field_name in skip_fields:
                continue
            field_details = self.entity.get_field(field_name)
            if field_details["type"] == "bool":
                field_value = xlate.convert_str_to_bool(field_value)
            elif field_details["type"] == "int":
                field_value = xlate.convert_any_to_int(field_value)
            setattr(self.entity, field_name, field_value)
        return True


# End File: automox/pignus/src/pignus/api/api_model_base.py
