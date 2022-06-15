"""Model Image Rest

"""
from pignus.models.rest_base import RestBase
from pignus.models.rest_container import RestContainer as Container
from pignus.models.image import FIELD_MAP


class RestImage(RestBase):

    def __init__(self, image: dict = None):
        super(RestImage, self).__init__()
        self.raw = image
        self.containers = {}
        self.build(FIELD_MAP, image)

    def __repr__(self) -> str:
        """Display a representation of the Image. """
        return "<Image %s:%s>" % (self.id, self.name)

    def build(self, FIELD_MAP: dict, image: dict) -> bool:
        """Extend the base build so we can hydrate the containers. """
        containers = image["containers"]
        super(RestImage, self).build(FIELD_MAP, image)
        for container_digest, container in containers.items():
            self.containers[container_digest] = Container(container)
        return True

    def get_containers(self) -> dict:
        """Get the image containers. """
        return self.containers

    def details(self) -> bool:
        """Display the details of the model. Mostly useful for debugging. """
        print(self)


# End File: automox/pignus/src/pignus/models/rest_image.py
