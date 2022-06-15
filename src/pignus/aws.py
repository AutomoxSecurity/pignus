"""AWS
A collection of aws commands related to container management and code build runners.

"""
import json

import boto3
import botocore

from pignus.models.image import Image
from pignus.models.image_build import ImageBuild
from pignus.utils import log
from pignus.utils import date_utils
from pignus.utils import misc_server
from pignus import misc
from pignus import settings


AWS_ACCOUNT = settings.server["AWS"]["ACCOUNT"]
AWS_REGION = settings.server["AWS"]["REGION"]
PIGNUS_KMS = settings.server["AWS"]["PIGNUS_KMS"]
CAN_DELETE_ECR = settings.options.get("AWS_ECR_DELETE")
PIGNUS_SYNC_JOB = "Pignus-Sync-Image"


def create_repository(image: Image) -> str:
    """Create an ECR repository in the local account, encrypted with the PIGNUS_KMS key. First
    checking first to see if the ECR repository already exists, returning the new ECR
    repository"s address.
    """
    can_create_ecr = settings.options.get("AWS_ECR_CREATE").value
    if not can_create_ecr:
        log.warning("This environment is not allowed to create ECR repositories.")
        return False

    try:
        client = boto3.client("ecr", region_name=AWS_REGION)
        exists = repository_exists(image)
        if exists:
            return "%s.dkr.ecr.%s.amazonaws.com" % (AWS_ACCOUNT, AWS_REGION)
        if not PIGNUS_KMS:
            log.error("Cannot create ECR repository, PIGNUS_KMS key is not set")
            return False
        client.create_repository(
            repositoryName=image.name,
            tags=[
                {"Key": "Team", "Value": "secops"},
                {"Key": "app", "Value": "pignus"},
            ],
            imageTagMutability="MUTABLE",
            imageScanningConfiguration={"scanOnPush": True},
            encryptionConfiguration={"encryptionType": "KMS", "kmsKey": PIGNUS_KMS},
        )
        log.info("Created repository: %s" % image.name, image=image)
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        exit(1)
        return False

    except client.exceptions.ClientError as e:
        log.error("Expired AWS credentials", exception=e)
        exit(1)

    except Exception as e:
        log.error(
            'Could not create ECR repository "%s"' % image.name,
            image=image,
            exception=e,
        )
        pass
    return "%s.dkr.ecr.%s.amazonaws.com" % (AWS_ACCOUNT, AWS_REGION)


def delete_repository(image: Image) -> str:
    """Delete an ECR repository in the local account."""
    if not CAN_DELETE_ECR:
        log.warning("This environment is now allowed to delete ECR repositories.")
        return

    try:
        client = boto3.client("ecr", region_name=AWS_REGION)
        exists = repository_exists(image)
        if not exists:
            log.warning(
                "Asked to delete a repository that already does not exist.",
                image=image,
                stage="delete-ecr",
            )
            return True
        client.delete_repository(repositoryName=image.name, force=False)
        log.info("Deleted repository: %s" % image, image=image)
        return True
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        return False
    except Exception as e:
        log.error(
            'Could not create ECR repository "%s"' % image,
            image=image,
            exception=e,
            stage="delete-ecr",
        )
        return False

# def delete_repository_tmp(name) -> str:
#     """Delete an ECR repository in the local account. """
#     client = boto3.client("ecr", region_name=AWS_REGION)

#     try:
#         client.delete_repository(
#             repositoryName=name,
#             force=False
#         )
#         log.info(
#             "Deleted repository: %s" % name)
#     except Exception as e:
#         log.error('Could not create ECR repository "%s"' % name, exception=e)
#         pass
#     return "%s.dkr.ecr.%s.amazonaws.com" % (AWS_ACCOUNT, AWS_REGION)


def repository_exists(image: Image) -> bool:
    """Check if a ECR repository exists in the local AWS account, returning the True if it does and
    False if it does not.
    """
    try:
        client = boto3.client("ecr", region_name=AWS_REGION)
        if client.describe_images(repositoryName=image.name):
            return True
        else:
            return False
    except botocore.exceptions.ClientError as e:
        log.warning(
            "Error in ECR repository exist check: %s" % image.name,
            image=image,
            stage="create-ecr",
            exception=e,
        )
        return False
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        return False


def set_repoisitory_iam_policy(image: Image) -> bool:
    """Set a repository IAM policy on the ECR repository, with a given image name ie, "automox/ws"
    @todo: This is primarily used by the web client, this needs to know the parent AWS Account that
    Pignus is running under.
    """
    secops_read_only = {
        "Version": "2008-10-17",
        "Statement": [
            {
                "Sid": "SecopsReadOnly",
                "Effect": "Allow",
                "Principal": {"AWS": "arn:aws:iam::123456789790:root"},
                "Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:DescribeImages",
                    "ecr:GetAuthorizationToken",
                    "ecr:GetDownloadUrlForLayer",
                ],
            }
        ],
    }
    policy = get_repository_iam_policy(image)
    if policy:
        statement = misc.compile_iam_statements(
            json.loads(policy["policyText"]), secops_read_only
        )
    else:
        # log.warning("Image %s has no prior policy" % image, image=image, stage="aws-ecr-policy")
        statement = secops_read_only

    try:
        client = boto3.client("ecr", region_name=AWS_REGION)
        client.set_repository_policy(
            registryId=AWS_ACCOUNT,
            repositoryName=image.name,
            policyText=json.dumps(statement),
            force=False,
        )
        return True
    except botocore.exceptions.ClientError as e:
        log.error('Could not apply IAM policy to "%s"' % image, exception=e, image=image)
        return False
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e, image=image)
        return False


def get_repository_iam_policy(image: Image) -> dict:
    """Set a repository IAM policy on the ECR repository, with a given image name ie, "automox/ws" """
    try:
        client = boto3.client("ecr", region_name=AWS_REGION)
        policy = client.get_repository_policy(
            repositoryName=image.name
        )
        return policy
    except client.exceptions.RepositoryPolicyNotFoundException as e:
        log.warning(
            'Could not find IAM policy for %s' % image,
            exception=e,
            image=image)
        return {}
    except botocore.exceptions.ClientError as e:
        log.error("Could not get IAM policy to Image %s" % image, exception=e, image=image)
        return False
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        return False

    return False


def build_container_import(image: Image, image_build: ImageBuild) -> bool:
    """Run a given Aws CodeBuild project with optional environment overrides.
    Known CodeBuild statuses "SUCCEEDED", "FAILED", "FAULT", "STOPPED", "TIMED_OUT"
    """
    repository = image_build.repository
    tag = image_build.tags[0]
    envs = [
        {"name": "REPOSITORY", "value": repository, "type": "PLAINTEXT"},
        {"name": "IMAGE", "value": image.name, "type": "PLAINTEXT"},
        {"name": "DIGEST", "value": image_build.digest, "type": "PLAINTEXT"},
        {"name": "TAG", "value": tag, "type": "PLAINTEXT"},
    ]

    # If the image comes from a different AWS account, inform the importer of that.
    aws_account = misc.get_origin_aws_account(repository)
    if aws_account and aws_account != AWS_ACCOUNT:
        envs.append(
            {"name": "FROM_AWS_ACCOUNT", "value": aws_account, "type": "PLAINTEXT"}
        )
    try:
        client = boto3.client("codebuild", region_name=AWS_REGION)
        build = client.start_build(
            projectName=PIGNUS_SYNC_JOB, environmentVariablesOverride=envs
        )
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        exit(1)
        return False
    except botocore.exceptions.ClientError as e:
        log.error("Credentials to AWS missing", exception=e)
        exit(1)
        return False

    build_id = build["build"]["id"]
    return build_id


def build_runner(build_name: str, image: Image, image_build: ImageBuild, wait=False) -> bool:
    """Run a given Aws CodeBuild project with optional environment overrides.
    Known CodeBuild statuses "SUCCEEDED", "FAILED", "FAULT", "STOPPED", "TIMED_OUT"
    """
    envs = [
        {"name": "IMAGE", "value": image.name, "type": "PLAINTEXT"},
        {"name": "DIGEST", "value": image_build.digest_local, "type": "PLAINTEXT"},
    ]
    if image_build.tags:
        envs.append({"name": "TAG", "value": image_build.tags[0], "type": "PLAINTEXT"})

    try:
        client = boto3.client("codebuild", region_name=AWS_REGION)
        build = client.start_build(
            projectName=build_name, environmentVariablesOverride=envs
        )
    except botocore.exceptions.ParamValidationError as e:
        log.error(
            "Error starting CodeBuild job for %s" % image,
            image=image,
            image_build=image_build,
            exception=e,
            envs=envs
        )
        return False
    build_id = build["build"]["id"]
    return build_id
    # if not wait:
    #     return build_id

    # ## Wait should be broken up
    # buildSucceeded = False
    # start = datetime.now()
    # counter = 0
    # while counter < 50:
    #     time.sleep(15)
    #     counter = counter + 1
    #     theBuild = client.batch_get_builds(ids=[build_id])
    #     build_status = theBuild["builds"][0]["buildStatus"]
    #     print("\t\t%s - %s" % (build_status, datetime.now() - start))
    #     setattr(image, "%s_ts" % field_scan_prefix, arrow.utcnow().datetime)
    #     if build_status == "SUCCEEDED":
    #         setattr(image, "%s" % field_scan_prefix, True)
    #         image.save()
    #         print("\tPassed: %s - %s:%s" % (build_name, image.name, image.tag))
    #         return True
    #     elif build_status in ["FAILED", "FAULT", "STOPPED", "TIMED_OUT"]:
    #         setattr(image, "%s" % field_scan_prefix, False)
    #         break
    # image.save()
    # print("%s:%s failed %s" % (image.name, image.tag, build_name))
    # return False


def get_build(image: Image, build_id: str) -> dict:
    """Get the details from an AWS CodeBuild job."""
    try:
        client = boto3.client("codebuild", region_name=AWS_REGION)
        client.batch_get_builds(ids=[build_id])
        the_build = client.batch_get_builds(ids=[build_id])
        return _unpack_build(build_id, the_build)
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        exit(1)
    except client.exceptions.ClientError as e:
        log.error("Expired AWS credentials", exception=e)
        exit(1)
    except Exception as e:
        log.error(
            "Could not get BuildId: %s for Image: %s" % (build_id, image),
            exception=e,
            image=image)
        return False


def _unpack_build(build_id: str, build_data: dict) -> dict:
    """Unpack the data returned from the AWS CodeBuild response into something more manageable.
    :unit-test: TestAws.test___unpack_build()
    """
    build_status = build_data["builds"][0]["buildStatus"]
    ret = {
        "id": build_id,
        "status": build_status,
        "start_time": date_utils.get_as_utc(build_data["builds"][0]["startTime"]),
        "end_time": None,
        "log_group": None,
        "log_stream": None,
    }
    if "groupName" in build_data["builds"][0]["logs"]:
        ret["log_group"] = build_data["builds"][0]["logs"]["cloudWatchLogs"]["groupName"]

    if "streamName" in build_data["builds"][0]["logs"]:
        ret["log_stream"] = build_data["builds"][0]["logs"]["cloudWatchLogs"]["streamName"]

    if "endTime" in build_data["builds"][0]:
        ret["end_time"] = date_utils.get_as_utc(build_data["builds"][0]["endTime"])

    return ret


def get_build_logs(build_info: dict) -> list:
    """Loads the log messages for a given build, from the result of the get_build function."""
    start_time = date_utils.get_aws_epoch(build_info["start_time"])
    log_stream_name = build_info['id'].replace(":", "/")
    try:
        client = boto3.client("logs", region_name=AWS_REGION)
        logs = client.get_log_events(
            startTime=start_time,
            logGroupName=build_info["log_group"],
            logStreamName=log_stream_name
        )
    except botocore.exceptions.NoCredentialsError as e:
        log.error("Credentials to AWS missing", exception=e)
        return False

    return logs["events"]


def put_parameter(parameter: str, value: str) -> bool:
    """Put an AWS SSM parameter, encrypted with the Pignus KMS key."""
    pignus_kms_arn = misc_server.get_kms_key_id()
    try:
        client = boto3.client("ssm", region_name=AWS_REGION)
        response = client.put_parameter(
            Name=parameter,
            Value=value,
            Type="SecureString",
            KeyId=pignus_kms_arn,
            Overwrite=True,
        )
        if not response:
            log.error("Encountered unknown error putting paramater.")
            return False
        log.info("Stored parameter: %s" % parameter)
        return True
    except botocore.exceptions.ClientError as e:
        log.error("Error putting parameter: %s" % parameter, exception=e)
        return False


def get_parameter(parameter: str) -> str:
    """Get an AWS SSM parameter."""
    try:
        client = boto3.client("ssm", region_name=AWS_REGION)
        response = client.get_parameter(
            Name=parameter,
            WithDecryption=True
        )
        return response["Parameter"]["Value"]
    except client.exceptions.ParameterNotFound as e:
        log.warning("Paramter: %s not found" % parameter, exception=e)
        return False
    except botocore.exceptions.ClientError as e:
        log.error("Error getting parameter: %s" % parameter, exception=e)
        return False


# End File: automox/pignus/src/pignus/aws.py
