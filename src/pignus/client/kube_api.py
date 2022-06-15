"""Kube Api
Connects to the Kube Rest Api for collecting data from a Kubernetes cluster from in or outside of
the cluster.

"""
import glom
import requests

from pignus.utils import log
from pignus.utils import mathy


class KubeApi:
    def __init__(self, api_server: str, token_file: str = None):
        """
        :unit-test: TestKubeApi.test____init__
        """
        self.kube_api = api_server
        self.token = None
        self.token_file = token_file

        if self.token_file:
            self._get_local_token()
        self.k8s_api_paths = {
            "pods": {
                "api": "/api/v1/namespaces/%(namespace)s/pods/",
                "containers_path": "spec.containers",
                "init_containers_path": "spec.initContainers",
            },
            "deployments": {
                "api": "/apis/apps/v1/namespaces/%(namespace)s/deployments/",
                "containers_path": "spec.template.spec.containers",
            },
            "statefulsets": {
                "api": "/apis/apps/v1/namespaces/%(namespace)s/statefulsets/",
                "containers_path": "spec.template.spec.containers",
            },
            "cronjobs": {
                "api": "/apis/batch/v1beta1/namespaces/%(namespace)s/cronjobs",
                "containers_path": "spec.jobTemplate.spec.template.spec.containers",
            },
        }

    def get_images(self, namespace="default", all_namespaces=False):
        """Get all unique images in a namespace. Currently supports pods, deployments, cronjobs,
        statefulsets. Need to add daemonsets, jobs.
        """
        if all_namespaces:
            namespaces = self.get_namespaces()
        else:
            namespaces = [namespace]

        pods_images = []
        deployments_images = []
        cronjobs_images = []
        statefulset_images = []

        for namespace in namespaces:
            pods_images += self.get_obect_images("pods", namespace)
            deployments_images += self.get_obect_images("deployments", namespace)
            # cronjobs_images += self.get_obect_images('cronjobs', namespace)
            # statefulset_images += self.get_obect_images('statefulsets', namespace)

        images = pods_images + deployments_images + cronjobs_images + statefulset_images
        unique_images = mathy.get_unique(images)
        return unique_images

    def get_pods(self, namespace="default", all_namespaces=False):
        if all_namespaces:
            namespaces = self.get_namespaces()
        else:
            namespaces = [namespace]

        pod_data = []
        for namespace in namespaces:
            namespace_pods = {
                "namespace": namespace,
                "pods": self.get_objects("pods", namespace),
            }
            pod_data.append(namespace_pods)
        return pod_data

    def get_namespaces(self) -> list:
        """Returns all namespaces."""
        namespaces = self.make_request("/api/v1/namespaces")

        ret = []
        for namespace in namespaces["items"]:
            ret.append(namespace["metadata"]["name"])

        return ret

    def get_objects(self, object_name: str, namespace: str) -> dict:
        """Get a k8s object from a given namespace, as long as it's supported in
        self.k8s_api_paths.
        """
        if object_name not in self._supported_k8s_apis():
            log.error('Unsupported object "%s"' % object_name)
            exit(1)

        api_path = self.k8s_api_paths[object_name]["api"] % {"namespace": namespace}
        response = self.make_request(api_path)
        return response

    def get_objects_all_namespaces(self, object_name: str):
        """Get a k8s object from a given namespace, as long as it's supported in
        self.k8s_api_paths.
        """
        if object_name not in self._supported_k8s_apis():
            print('Unsupported object "%s"' % object_name)
            exit(1)
        self._load_namespaces()
        data = []
        for namespace in self.namespaces:
            api_path = self.k8s_api_paths[object_name]["api"] % {"namespace": namespace}
            response = self.make_request(api_path)
            if response["items"]:
                data += response["items"]
        return data

    def get_obect_images(self, object_name: str, namespace: str) -> list:
        """Get all images for a given supported k8s object type for a particular namespace."""
        if object_name not in self._supported_k8s_apis():
            print('Unsupported object "%s"' % object_name)
            exit(1)
        objects = self.get_objects(object_name, namespace)

        init_images = None
        if "init_containers_path" in self.k8s_api_paths[object_name]:
            init_images = self.k8s_api_paths[object_name]["init_containers_path"]

        images = self._get_object_container_images(
            objects, self.k8s_api_paths[object_name]["containers_path"], init_images
        )

        return images

    def make_request(self, url: str, payload={}) -> dict:
        """Makes a request to the K8s API, returning the result as a dict."""
        headers = {}
        verify = True
        if self.token:
            headers = {
                "Authorization": "Bearer %s" % self.token,
            }
            verify = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        full_url = "%s%s" % (self.kube_api, url)
        request_args = {
            "method": "GET",
            "url": full_url,
            "params": payload,
            "headers": headers,
            "verify": verify,
        }
        try:
            response = requests.request(**request_args)
        except requests.exceptions.ConnectionError:
            log.error("Could not connect to Kube API server %s" % self.kube_api)
            exit(1)
        if response.status_code >= 400:
            log.error("K8s Responded <%s> %s" % (response.status_code, response.text))
            exit(1)

        parsed = response.json()

        return parsed

    def event_log(self):
        """Get the Kubernetes event log log."""
        # Get all namespaces
        if True:
            self._load_namespaces()

        # self.logger.info('Getting events for %s namespaces' % self.namespaces)
        events_items = []

        for namespace in self.namespaces:
            url = "/apis/events.k8s.io/v1beta1/namespaces/%s/events" % namespace
            params = {}
            events = self.make_request(url, params)
            for event in events["items"]:
                events_items.append(event)
        return events_items

    def _get_object_container_images(
        self, k8s_object, api_path_to_containers: str, api_path_to_init_containers=None
    ) -> list:
        """Take a k8s object and a glom path and return unique images from that k8s object's
        details.
        api_path_to_containers ex "spec.template.spec" will read x['spec']['template']['spec']
        """
        images = []
        for k8_item in k8s_object["items"]:
            containers = glom.glom(k8_item, api_path_to_containers)
            # If we have init containers, get them too.
            if api_path_to_init_containers:
                try:
                    containers += glom.glom(k8_item, api_path_to_init_containers)
                except glom.PathAccessError:
                    pass

            # Collect just the image
            for container in containers:
                images.append(container["image"])

        images = mathy.get_unique(images)
        return images

    def _supported_k8s_apis(self):
        return self.k8s_api_paths.keys()

    def _load_namespaces(self):
        """Load all cluster namespaces into a list located at self.namespaces."""
        if not self.namespaces:
            self.namespaces = self.get_namespaces()

    def _get_local_token(self):
        """Get the local token file."""
        if not self.token_file:
            return False
        f = open(self.token_file, "r")
        token = f.read().replace("\n", "")
        self.token = token
        f.close()
        return True


# End file: automox/src/pignus/client/kube_api.py
