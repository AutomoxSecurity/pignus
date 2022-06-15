"""Settings
Primary settings/ configuration for all Pignus apps.
Many of these details can be found via the API at /details/.

Testing
    Unit Tests: automox/pignus/tests/unit/test_settings.py
    100% Test Coverage!

"""
import os

from pignus.version import __version__
from pignus.utils import client_misc


global general
general = {
    "VERSION": __version__,
    "LOG_LEVEL": os.environ.get("PIGNUS_LOG_LEVEL", "DEBUG"),
}

global server
server = {
    "VERSION": __version__,
    "ENVIRONMENT": os.environ.get("PIGNUS_RELEASE_ENV", "PROD"),
    "PATH": os.environ.get("PIGNUS_PATH"),
    "SENTRY": {
        "SCAN_LIMIT": None,
        "SCAN_INTERVAL_HOURS": None,
        "SYNC_LIMIT": None,
    },
    "DATABASE": {
        "USER": os.environ.get("PIGNUS_DB_USER"),
        "PASS": os.environ.get("PIGNUS_DB_PASS"),
        "NAME": os.environ.get("PIGNUS_DB_NAME", "pignus"),
        "HOST": os.environ.get("PIGNUS_DB_HOST")
    },
    "AWS": {
        "ACCOUNT": os.environ.get("PIGNUS_AWS_ACCOUNT"),
        "REGION": os.environ.get("PIGNUS_AWS_REGION", "us-west-2"),
        "PIGNUS_KMS": os.environ.get("PIGNUS_AWS_KMS"),
        "AWS_LOCAL_ECR": "%s.dkr.ecr.%s.amazonaws.com" % (
            os.environ.get("PIGNUS_AWS_ACCOUNT"),
            os.environ.get("PIGNUS_AWS_REGION", "us-west-2"))
    },
    "KEYS": {
        "PUBLIC": None,
        "PRIVATE": None
    }
}

global client
client = {
    "VERSION": __version__,
    "API_UA": client_misc.get_client_api_ua(),
    "API_URL": client_misc.get_client_api_url(),
    "API_KEY": os.environ.get("PIGNUS_API_KEY", None),
    "KUBE_API": os.environ.get("PIGNUS_THEIA_KUBE_API", None),
    "KUBE_TOKEN_FILE": os.environ.get("THEIA_KUBE_TOKEN_FILE", None),
    "AWS": {
        "ACCOUNT": os.environ.get("PIGNUS_AWS_ACCOUNT", None),
    }
}

# These settings are just defaults, they should be loaded from the database
global options
options = {}

global content
content = {
    "path": None,
    "method": None,
    "user-agent": None,
    "x-forwarded-for": None,
    "query_string_parameters": {},
    "user": None,
    "user_perms": [],
    "api-key": None
}

global context
context = {}

global request
request = {}

global db
db = {}


# End File: automox/pignus/src/pignus/settings.py
