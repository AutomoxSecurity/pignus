"""Image Add
Handles adding images and containers to the Pignus database.

"""
from pignus.utils import log
from pignus import aws
from pignus import settings
from pignus.models.image import Image
from pignus.models.image_build import ImageBuild


AWS_ACCOUNT = settings.server["AWS"]["ACCOUNT"]
AWS_REGION = settings.server["AWS"]["REGION"]


def add(image_dict: dict, fields: dict = {}) -> dict:
    """Add an image and container into the Pignus database."""
    ret = {
        "image": None,
        "container": None,
        "success": True
    }

    # See if image already exists in the Pignus database
    image = Image()
    image.get_by_name(image_dict["name"])
    if not image.get_by_name(image_dict["name"]):
        image = Image()
        image.name = image_dict['name']
        if "repository" in image_dict:
            image.repositories = [image_dict["repository"]]
        image.save()
        if "regression-test" in image.name:
            log.warning(
                "Not creating repository for %s" % image.name,
                image=image,
                stage="image-add",
            )
        else:
            aws.create_repository(image)
        log.info("Image added", image=image, stage="image-add")
    else:
        log.info("Image found", image=image, stage="image-add")

    # Handle Image repositories
    if not image.repositories:
        image.repositories = []
    if image_dict["repository"] not in image.repositories:
        image.repositories.append(image_dict["repository"])
        image.save()

    image.get_builds()
    # Add the image build if it doesn't exist
    if image_dict["digest"] and image_dict["digest"] not in image.builds:
        image_build = image_build_add(image, image_dict)
    elif not image_dict["digest"]:
        log.error(
            "Missing digest, cannot create container",
            image=image,
            stage="image-add")
        image_build = False
    else:
        image_build = image.builds[image_dict["digest"]]
        log.info("Container found", image_build=image_build, stage="image-add")

    if not image_build:
        ret["success"] = False

    ret["image"] = image
    ret["image_build"] = image_build

    return ret


def image_build_add(image: Image, image_in: dict) -> ImageBuild:
    """Attempt to add a  container to the Pignus database, if it already exists, return it."""
    image.get_builds()
    add_image_build = False

    if "digest" not in image_in and not image_in["digest"]:
        log.warning("Cannot create container without digest")
        return False

    if image_in["digest"] not in image.builds:
        add_image_build = True

    if add_image_build:
        log.debug("Adding container", image=image, stage="image-add")
        image_build = ImageBuild()
        image_build.digest = image_in["digest"]
        image_build.repository = image_in["repository"]
        image_build.image_id = image.id
        image_build.tags = [image_in['tag']]
        image_build.sync_flag = True
        image_build.save()
        log.info(
            "Container added for image",
            image=image,
            image_build=image_build,
            stage="image-add")
    else:
        image_build = image.builds[image_in["digest"]]
        log.info(
            "Container already exists",
            image=image,
            container=image_build,
            stage="image-add")

    return image_build


# End File: automox/pignus/src/pignus/image_add.py
