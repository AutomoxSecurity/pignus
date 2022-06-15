"""Pignus Lambda and Pignus Theia entry points.

"""
import argparse
import os
import json
import traceback
import sys

from pignus.pignus_api import PignusApi
from pignus.pignus_sentry import PignusSentry
from pignus.pignus_theia import PignusTheia
from pignus import misc
from pignus.utils import log


def handler(event: dict, context):
    """Lambda event handler entry point."""
    log.debug("Event: %s" % event)

    # Route the ApiGateway requests
    if context.function_name == "Pignus-Gateway":
        # In debug environments let the app crash without handling the exception for logging
        debug_env = os.environ.get("PIGNUS_DEBUG")
        if debug_env == "true":
            log.debug("Running in DEBUG Environment")
            pignus_api = PignusApi(event, context)
            response = pignus_api.run()
            return response
        else:
            # Production mode should catch all errors so the client doesnt get hung up on
            try:
                pignus_api = PignusApi(event, context)
                response = pignus_api.run()
                return response
            except Exception as e:
                log.error("Pignus Api run time error",
                    exception=e
                )
                log.error(e)
                log.error(traceback.format_exc())
                log.error(sys.exc_info()[2])
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                    },
                    "body": "Error",
                    "isBase64Encoded": False,
                }

    # Route Sentry requests
    elif context.function_name == "Pignus-Sentry":
        try:
            log.info("Using Sentry handler")
            pignus_sentry = PignusSentry(event, context)
            response = pignus_sentry.run()
        except Exception as e:
            log.error("Pignus Sentry run time error",
                exception=e
            )
            exit(1)
    else:
        log.error("Unknown context error")
        print("Error")
        exit(1)
    log.info("Request completed successfully")
    return json.dumps(response)


def theia_handler():
    """Theia handler, starts the Theia application for a cluster check-in"""
    cluster_name = os.environ.get("PIGNUS_THEIA_CLUSTER")
    PignusTheia().run(cluster_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.error("Missing required arguments.")
        exit(1)

    if sys.argv[1] == "cluster-check-in":
        theia_handler()

# End File: automox/pignus/docker/src/app.py
