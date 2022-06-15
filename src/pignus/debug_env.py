"""
"""
import os
import json

from pignus.pignus_api import PignusApi
from pignus import misc
from pignus.utils import log


ADMIN_KEY = os.environ.get("PIGNUS_API_KEY_DEV_ROLE_ADMIN")
CLUSTER_KEY = os.environ.get("PIGNUS_API_KEY_DEV_ROLE_CLUSTER")


class DebugEnv:
    def __init__(self):
        self.cluster_name = "test-cluster"
        self.user_name = "test-cluster"
        self.cluster_key = CLUSTER_KEY

    def create_all(self):
        self.create_cluster()
        self.create_user()
        self.create_images()

    def create_cluster(self):
        event = {
            "path": "/cluster",
            "httpMethod": "POST",
            "headers": {
                "x-api-key": ADMIN_KEY
            },
            "queryStringParameters": {
                "create": True,
            },
            "body": {
                "name": self.cluster_name,
            }
        }
        data = self.run_debug_event(event)
        log.info("Created Cluster: %s" % self.cluster_name)

    def create_user(self):
        """Create an ApiKey."""
        event = {
            "path": "/user",
            "httpMethod": "POST",
            "headers": {
                "x-api-key": ADMIN_KEY
            },
            "queryStringParameters": {
                "create": True
            },
            "body": {
                "role_id": 3,
                "name": self.user_name,
            }
        }
        data = self.run_debug_event(event)
        if not data:
            print("ERROR")
            exit(1)
        event = {
            "path": "/api-key",
            "httpMethod": "POST",
            "headers": {
                "x-api-key": ADMIN_KEY
            },
            "queryStringParameters": {
                "create": True
            },
            "body": {
                "user_id": data["data"]["object"]["id"],
            }
        }
        data = self.run_debug_event(event)
        self.cluster_key = data["data"]["object"]["key"]
        log.info("Created %s with api-key: %s" % (self.user_name, self.cluster_key))

    def create_images(self):
        images = [
            {
                "name": "wordpress",
                "repository": "docker.io",
                "containers": [
                    {
                    "tag": "cli-php8.1",
                    "digest": "70039ffe31e6ae02d97330ae80f7aa9f0d5236999d4a64dcf3aed5bd140bb3c1",
                    },
                    {
                    "tag": "latest",
                    "digest": "dc19e32363b405a82a2ad0cb6809664f4a1bf7149216e1ae2ffbeae2268c4024"
                    }
                ]
            },
            {
                "name": "ubuntu",
                "repository": "docker.io",
                "containers": [
                    {
                        "tag": "16.04",
                        "digest": "cf25d111d193288d47d20a4e5d42a68dc2af24bb962853b067752eca3914355e",
                    },
                    {
                        "tag": "14.04",
                        "digest": "12d9fa858f255e4b70827aff83e8ce37b6fcaddaf6732276aa1f0763402f4fdc"
                    },
                    {
                        "tag": "ubuntu:groovy-20210514",
                        "digest": "328a4beb0442f2d7200c4a26bee07bdbdc4b249707d933967d3400d552db72e8"
                    },
                    {
                        "tag": "bionic-20180710",
                        "digest": "74f8760a2a8b28abade3fcbcdb6998543f1d9b4a6fb61463c10adc0765c3cb12"
                    },
                ]
            },
            {
                "name": "busybox",
                "repository": "docker.io",
                "containers": [
                    {
                        "tag": "stable",
                        "digest": "ce06da2e3e24e4ac99f6da067bcab57e3dcc2ea4582da16e5d97003c32a6fa8c",
                    },
                    {
                        "tag": "1.35",
                        "digest": "db5bbbe5e2896cc32e9628c7b31ad33cad20362006e803b26b41e4c88cf715cf"
                    },
                ]
            },
            {
                "name": "politeauthority/the-carolina-reaper",
                "repository": "docker.io",
                "containers": [
                    {
                        "tag": "latest",
                        "digest": "fa6af2041e78aaf80fb8a195d9f9d70300a368880fdd9dfe296885020ed9cb32",
                    },
                ]
            },
            {
                "name": "kennethreitz/httpbin",
                "repository": "docker.io",
                "containers": [
                    {
                        "tag": "latest",
                        "digest": "b138b9264903f46a43e1c750e07dc06f5d2a1bd5d51f37fb185bc608f61090dd",
                    },
                ]
            },
            {
                "name": "prometheus/alertmanager",
                "repository": "quay.io",
                "containers": [
                    {
                        "tag": "v0.21.0",
                        "digest": "24a5204b418e8fa0214cfb628486749003b039c279c56b5bddb5b10cd100d926",
                    },
                ]
            },
        ]

        event = {
            "path": "/check-in",
            "httpMethod": "POST",
            "headers": {
                "x-api-key": self.cluster_key
            },
            "queryStringParameters": {},
            "body": {
                "cluster": self.cluster_name,
            }
        }


        for image_dict in images:
            for container in image_dict["containers"]:
                this_event = event
                this_event["body"]["name"] = image_dict["name"]
                this_event["body"]["repository"] = image_dict["repository"]
                this_event["body"]["tag"] = container["tag"]
                this_event["body"]["digest"] = container["digest"]
                data = self.run_debug_event(this_event)
                log.info("Made Image/Build %s:%s" % (
                    this_event["body"]["name"],
                    this_event["body"]["tag"]))


    def run_debug_event(self, event, print_this=False):
        """Run an event against the local Pignus Api."""
        api = PignusApi(event)
        response = api.run()
        data = json.loads(response["body"])
        if print_this:
            misc.pretty_print(data)
        return data
