"""Pignus Theia
This class is intended to run from the K8s cronjob inside the cluster. It gathers the data from the
K8s api and reports it off to the Pignus api.

"""
import time

from pignus.client.rest import Rest
from pignus.client.kube_api import KubeApi
from pignus.utils import log
from pignus.utils import xlate
from pignus.utils import mathy
from pignus.utils import client_misc
from pignus import settings
from pignus import misc
from pignus.version import __version__


class PignusTheia:
    def __init__(self):
        """
        """
        self.check_in_success = 0
        self.check_in_containers_processed = 0
        self.kube_api = KubeApi(
            settings.client["KUBE_API"],
            settings.client["KUBE_TOKEN_FILE"],
        )
        self.pignus_api = Rest()
        self.process_start = time.time()

    def run(self, cluster_name: str = None) -> dict:
        """Entry point for cluster check in. Connects to the Kubernetes API, pulling all images
        currently deployed to a cluster. Getting all unique images within the cluster and checking
        them into the Pignus Api as present in the cluster.
        """
        log.info("Pignus Theia v%s" % __version__)
        log.info("User Agent: %s" % client_misc.get_client_api_ua())
        log.info("Pignus Api: %s" % self.pignus_api.api_url)
        log.info("Cluster Check-in: %s" % cluster_name)

        self.cluster_name = cluster_name
        if not self.cluster_name:
            self.cluster_name = client_misc.get_client_theia_cluster()
            if not self.cluster_name:
                log.error("Missing cluster name for check in")
                exit(1)

        self.get_pod_data()

        check_ins = self.send_check_ins()
        if not check_ins:
            log.erorr("Failed to send cluster check-in")
            exit(1)

        msg = "%s/%s %s%% check-ins successful" % (
            self.check_in_success,
            len(self.check_in_data),
            mathy.percentage(self.check_in_success, len(self.check_in_data)),
        )
        self.process_end = time.time()
        self.total_time = self.process_end - self.process_start
        log.info("Process time: %s seconds" % round(self.total_time, 2))
        return msg

    def get_pod_data(self) -> bool:
        """Get all pods running in the cluster from the Kubernetes api and prune the data into list
        of unique images, with the data organized for submission to the Pignus api.
        """
        pod_data = self.kube_api.get_pods(all_namespaces=True)
        # pod_data = self.kube_api.get_pods(namespace="secops")
        pruned_data = self.prune_pod_data(pod_data)
        self.check_in_data = pruned_data
        return True

    def prune_pod_data(self, pod_data: list) -> list:
        """Prune the data returned from the K8s api so we're left with just the data we want to
        return to Pignus to complete the Check-In.
        :unit-test: test__prune_pod_data
        """
        pruned_data = []
        log.info("Found %s namespaces" % len(pod_data))
        for namespace in pod_data:
            for item in namespace["pods"]["items"]:
                if "containerStatuses" not in item["status"]:
                    log.warning("Missing status, skipping")
                    continue
                for container in item["status"]["containerStatuses"]:
                    parsed = misc.parse_image_url(container["image"])
                    if parsed["name"] == "":
                        log.error("[Error] with image")
                        continue
                    container_details = {
                        "name": parsed["name"],
                        "repository": parsed["repository"],
                        "tag": parsed["tag"],
                        "digest": xlate.get_digest(container["imageID"]),
                    }
                    pruned_data.append(container_details)

        pruned_data = mathy.get_unique(pruned_data)
        return pruned_data

    def send_check_ins(self) -> bool:
        """Send all Images found to the Pignus Api for Check-In. Currently each Image is sent as a
        separate request, this could be optimized.
        """
        log.info("Checking in %s images" % len(self.check_in_data))

        for image_data in self.check_in_data:
            self.check_in_containers_processed += 1
            self.send_check_in(image_data)

        return True

    def send_check_in(self, image_data: dict) -> bool:
        """Verify the data pulled from the K8s api for a single Image and report it to the Pignus
        api.
        :unit-test: test__send_check_in
        """
        response = self.pignus_api.check_in_post(image_data, self.cluster_name)

        if not response:
            log.error("Pignus Responded: %s" % response)
            return False

        log.info(
            "%s/%s\tCheck-In Success: %s"
            % (
                self.check_in_containers_processed,
                len(self.check_in_data),
                image_data["name"],
            )
        )
        self.check_in_success += 1
        return True


# End File: automox/src/pignus/pignus_theia.py
