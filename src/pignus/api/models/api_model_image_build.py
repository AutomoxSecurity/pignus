"""Api Model Image Build
/image-build

"""
from pignus.api.models.api_model_base import ApiModelBase
from pignus.models.image_build import ImageBuild


class ApiModelImageBuild(ApiModelBase):
    def __init__(self, event: dict):
        super(ApiModelImageBuild, self).__init__(event)
        self.model = ImageBuild
        self.delete_destroy = True
        self.modifiable_fields = [
            "maintained", "sync_flag", "sync_enabled", "scan_flag", "scan_enabled"]
        self.model_url = "/image-build"
        self.perms = {
            "GET": "list-images",
            "POST": "post-images",
            "DELETE": "delete-images"
        }

# End File: automox/pignus/src/pignus/api/models/api_model_image_build.py
