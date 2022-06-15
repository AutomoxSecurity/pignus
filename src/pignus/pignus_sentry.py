"""Pignus Sentry

"""
import argparse
import json

from pignus.sentry.image_rectify import ImageRectify
from pignus.sentry.image_sync import ImageSync
from pignus.sentry.image_scan import ImageScan
from pignus.sentry.image_cron import ImageCron
from pignus.sentry.image_auth import ImageAuth
from pignus.utils.auth import Auth
from pignus.utils import log
from pignus.utils import misc_server
from pignus.utils.migrate import Migrate
from pignus import settings
from pignus import debug


class PignusSentry:
    def __init__(self, event: dict, context=None):
        self.response = {
            "actions": [],
            "status": "Success",
            "message": "",
            "status_code": 200,
            "data": {},
        }
        self.request_obj = None
        self.event = event
        if "verbosity" not in self.event:
            self.event["verbosity"] = None
        settings.request = event
        settings.context = context

    def migrate_db(self):
        """Create the database and establish the connection. """
        log.info("Running database init")
        return Migrate().run()

    def test(self):
        """Place to run development tests more easily. """
        debug.run()
        return True

    def run(self) -> dict:
        """Primary application entry point. """
        if self.event["verbosity"]:
            settings.server["LOG_LEVEL"] = self.event["verbosity"]

        self.handle_request()

        try:
            body = json.dumps(self.response)
        except TypeError:
            log.error("Cannot create JSON from response", response=self.response)
            self.response["status_code"] = 500
            body = None

        http_response = {
            "statusCode": self.response["status_code"],
            "body": body,
            "isBase64Encoded": False,
        }

        if self.response["interface"] in ["cli", "cli-api"]:
            return self.response
        else:
            return http_response

    def handle_request(self) -> bool:
        """Application router, sending requests to their desired destination."""
        self.response["interface"] = "cli"

        if "action" not in self.event:
            log.error("Pignus Sentry requires an action.")
            exit(1)

        # Run debug routine
        if self.event['action'] == "debug":
            self.test()
            return True

        # Run database migration
        if self.event['action'] == "migrate":
            migrated = self.migrate_db()
            self.response["message"] = migrated["data"]
            return True

        misc_server.set_db()
        if self.event['action'] == "create-user":
            misc_server.set_keys()
            user = Auth().create_user()
            log.info("Created User with api key: %s" % user["api_key"])
            return True

        elif self.event['action'] == "rotate-keys":
            misc_server.set_keys()
            Auth().rotate_key_pair()
            return True

        elif self.event['action'] == "auth":
            ImageAuth().run()
            return True

        # Sentry routines
        # Handle Cron routine
        elif self.event['action'] == "cron":
            ImageCron().run_cluster_cve()
            return True

        # Handle Sync routine
        elif self.event['action'] == "sync":
            ImageSync().run()
            return True

        # Handle Scan routine
        elif self.event['action'] == "scan":
            ImageScan().run()
            return True

        # Handle Rectify routine
        elif self.event['action'] == "rectify":
            x = ImageRectify().run()
            print(x)
            return True

        # Handle All routines
        elif self.event["action"] == "all":
            # Rectify Ops
            rectify_response = ImageRectify().run()
            self.response["data"]["rectify"] = rectify_response

            # Sync Ops
            ImageSync().run()

            # Scan Ops
            ImageScan().run()
            self.response["status"] = "Success"
            return True

        else:
            msg = 'No actions performed. Unknown action: "%s"' % (self.event["action"])
            self.response["status_code"] = 400
            self.response["status"] = "Error"
            self.response["message"] = msg
            log.error(msg, event=self.event, context=settings.context)
            return False

        return True


def cli_parse() -> dict:
    """Cli argument parse."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        default=False,
        help="Operation to run. all, add, sync, scan or rectify")
    parser.add_argument(
        "-v",
        "--verbosity",
        default="info",
        nargs="?",
        help="CVE number to search for")
    args = parser.parse_args()
    ret = {
        'action': args.action,
        'verbosity': args.verbosity,
    }
    return ret


if __name__ == "__main__":
    event = cli_parse()
    PignusSentry(event).run()

# End File: automox/pignus/src/pignus/pignus-sentry.py
