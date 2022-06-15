"""Client Misc

Testing
Unit Tests at automox/pignus/tests/unit/utils/test_client_misc.py

"""

import os

import arrow

from pignus.utils import date_utils
from pignus.version import __version__


def get_client_api_ua() -> str:
    """Get the Client User Agent str to set by default.
    :unit-test: test__get_client_api_ua
    """
    user_agent = "PignusClient/%s - %s" % (
        __version__,
        os.environ.get("PIGNUS_API_UA", "Unknown"))
    return user_agent


def get_client_api_url() -> str:
    """Get client Pignus api url to set by default.
    :unit-test: test__get_client_api_url
    """
    default = "https://pfvxhjjm5n.ext.automox.com"
    api_url = os.environ.get("PIGNUS_API_URL", default)
    return api_url


def get_client_theia_cluster() -> str:
    """Get the Pignus Theia cluster."""
    cluster = os.environ.get("PIGNUS_THEIA_CLUSTER")
    return cluster


def fmt_list(the_list: list) -> str:
    """Concact a list as a comma separated string"""
    if not the_list:
        return ""
    return ", ".join(the_list)


def fmt_date(the_date: arrow.arrow.Arrow) -> str:
    """Format a date by showing the human relatable time format, as well as the full date stamp."""
    if not the_date:
        return None
    the_str = "%s\t(%s)" % (
        date_utils.human_date(the_date),
        the_date
    )
    return the_str


def fmt_short_digest(digest):
    if not digest:
        return None
    return digest[:12]

# End File: automox/pignus/src/pignus/utils/client_misc.py
