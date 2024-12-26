from typing import List
import time
import yaml
from kubernetes.stream import stream
import kubernetes
from utils import log
from kubernetes import client
from kubernetes import config
from openshift.dynamic import DynamicClient
from openshift.dynamic import ResourceInstance

class ExternalPlatformLib(object):
    """
    This is a python library which provides basic functions to CRUD operations for different resources for
    Kubernetes based applications.
    The library provides the ability to perform operations with cloud resources. An important feature is that
    the presented functions do not interrupt the execution of the script at runtime - if an some exception is
    appear, the execution of the script will continue, informing about the error in logs.
    This is done for the convenience of using the library in pipelines, when there are often situations of
    absence or presence of resources that must be skipped in the script.
    """

    def __init__(self, token=None, host=None, kubeconfig=None):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if token and host:
                self._token = token
                self._host = host
                self._api_config = self.__build_api_config()
                k8s_api_client = client.ApiClient(self._api_config)
            elif kubeconfig:
                k8s_api_client = self.get_kubernetes_api_client(config_file=kubeconfig)
            # log("... K8S Client configured ...")
            self.dyn_client: DynamicClient = DynamicClient(k8s_api_client)
            self.k8s_core_v1_client = client.CoreV1Api(k8s_api_client)
            self.k8s_apps_v1_client = client.AppsV1Api(k8s_api_client)
            self.k8s_api_ext_v1_client = client.ApiextensionsV1Api(k8s_api_client)
            self.custom_objects_api = client.CustomObjectsApi(k8s_api_client)
            self.rbac_authorization = client.RbacAuthorizationV1Api(k8s_api_client)
            self.k8s_core_api = client.CoreApi(k8s_api_client)
            self.k8s_apis_api = client.ApisApi(k8s_api_client)
            self.ext_v1beta1_api = client.ExtensionsV1beta1Api(k8s_api_client)
            self.net_v1beta1_api = client.NetworkingV1beta1Api(k8s_api_client)
            self.net_v1_api = client.NetworkingV1Api(k8s_api_client)
            self.policy_v1beta1_api = client.PolicyV1beta1Api(k8s_api_client)
            self.api_version = client.VersionApi(k8s_api_client)
            self.api_registration = client.ApiregistrationV1Api(k8s_api_client)
        except Exception as e:
            if e.status == 401:
                log('... Can not initialize ExternalPlatformLib library. Please check token is not expired! ... ')
            else:
                log(f'... Some Exception is occured.\n{e}')

    def __build_api_config(self):
        configuration = client.Configuration()
        configuration.host = self._host
        configuration.verify_ssl = False
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.api_key['authorization'] = self._token
        return configuration

    def get_kubernetes_api_client(self, config_file, context=None, persist_config=True):
        try:
            config.load_incluster_config()
            return kubernetes.client.ApiClient()
        except config.ConfigException:
            return kubernetes.config.new_client_from_config(config_file=config_file,
                                                            context=context,
                                                            persist_config=persist_config)

    def check_kubernetes_version(self):
        version_info = self.api_version.get_code().to_dict()
        git_version = version_info["git_version"]
        if git_version[0] == 'v':
            git_version = git_version[1:]
        return git_version

    def parse_yaml_from_file(self, file_path):
        """
        The function parses YAML template by provided path for file via `file_path` parameter and returns body returns in
        dictionary format. Used for transform a YAML template into a request body.
        """
        return yaml.safe_load(open(file_path))

    def list_cluster_namespaces(self):
        """"
        Function returns list created namespaces in the cluster.
        """
        list_namespaces = self.k8s_core_v1_client.list_namespace()
        namespaces = []
        for namespace in list_namespaces.items:
            namespaces.append(namespace.metadata.name)
        return namespaces

    def is_namespace_exist(self, name):
        """
        The function returns whether a namespace with the specified name exists.
        """
        try:
            self.k8s_core_v1_client.read_namespace(name=name)
            log(f'... Yes, namespace {name} is exist! ... ')
            return True
        except Exception as e:
            log(f'... No, Namespace {name} is not exist! ... \n{e}')
            return False

    def create_namespace(self, name):
        """
        The function creates the namespace in the cloud.
        """
        try:
            body = dict(
                apiVersion='v1',
                kind='Namespace',
                metadata=dict(
                    name='name'
                )
            )
            body.get('metadata').update(name=name)
            self.k8s_core_v1_client.create_namespace(body=body)
            log(f'... Namespace {name} is created successfully!')
        except Exception as e:
            log(f'... Namespace {name} is not created!\n{e}')
            exit(1)

    def create_all_namespaces(self, array_names: list):
        """
        The function creates a list of namespaces in the cloud.
        `array_names` parameter specifes the list of namespaces names should be created.
        """
        for name in array_names:
            self.create_namespace(name)
        log('... All Namespaces are created!')

    def check_all_namespaces_created(self, array_names: list):
        """
        The function checks all namespaces created from specified names. If condition is true - it returns True.
        """
        count = 0
        list_count = len(array_names)
        for name in array_names:
            try:
                if(self.get_namespace(name)):
                    count += 1
                    log(f'Namespace {name} is created successfully!')
            except:
                log(f'Namespace {name} is not created!')
        if(list_count == count):
            return True

    def delete_namespace_with_timeout(self, name: str):
        """
        The function deletes the namespace by specified name and wait specified timeout.
        """
        timeout = 300
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            try:
                is_exist = self.is_namespace_exist(name)
                if is_exist == False:
                    log(f'... Namespace doesn\'t exist, nothing to delete, exit script! ...')
                    return
                self.delete_namespace(name)
                time.sleep(30)
                is_exist = self.is_namespace_exist(name)
            except Exception as e:
                print(e)
                continue
            if is_exist == False:
                log(f'... Namespace removal successfuly completed! ...')
                return

    def delete_all_namespaces(self, array_names: list):
        """
        The function deletes a list of namespaces in the cloud.
        `array_names` parameter specifes the list of namespaces names should be deleted.
        """
        for name in array_names:
            self.delete_namespace(name)
        log('... All Namespaces are deleted!')

    def annotate_namespace_uid_group(self, namespace: str, uid: str, group: str):
        """
        The function patch Namespace in the cloud by specified user, group.
        """
        project_body = [
            {
                'op': 'replace',
                'path': '/metadata/annotations/openshift.io~1sa.scc.uid-range',
                'value': ''
            }
        ]
        project_body[0].update(value=uid)
        self.k8s_core_v1_client.patch_namespace(namespace, project_body)

        project_body = [
            {
                'op': 'replace',
                'path': '/metadata/annotations/upplemental~1groups',
                'value': ''
            }
        ]
        project_body[0].update(value=group)
        self.k8s_core_v1_client.patch_namespace(namespace, project_body)
    
    def annotate_namespace_node_selector(self, namespace: str, value: str):
        """
        The function patch Namespace in the cloud by specified node selector.
        """
        project_body = [
            {
                'op': 'replace',
                'path': '/metadata/annotations/openshift.io~1node-selector',
                'value': ''
            }
        ]
        project_body[0].update(value=value)
        try:
            self.k8s_core_v1_client.patch_namespace(namespace, project_body)
            log(f'... Namespace {namespace} is annotated by following node selector {value}! ... ')
        except Exception as e:
            log(f'... Namespace {namespace} is not annotated! ... \nSome exception is occured: {e}')

    def annotate_namespace_labels(self, namespace: str, value: str, key='pod-security.kubernetes.io~1enforce'):
        """
        The function patch Namespace in the cloud by specified label.
        """
        project_body = [
            {
                'op': 'replace',
                'path': f'/metadata/labels/{key}',
                'value': ''
            }
        ]
        project_body[0].update(value=value)
        try:
            self.k8s_core_v1_client.patch_namespace(namespace, project_body)
            log(f'... Namespace {namespace} is annotated by following label: {key}:{value}! ... ')
        except Exception as e:
            log(f'... Namespace {namespace} is not annotated! ... \nSome exception is occured: {e}')

    def remove_namespace_label(self, namespace: str, key='pod-security.kubernetes.io~1enforce'):
        """
        The function delete label in specified Namespace.
        """
        project_body = [
            {
                'op': 'remove',
                'path': f'/metadata/labels/{key}'
            }
        ]
        try:
            self.k8s_core_v1_client.patch_namespace(namespace, project_body)
            log(f'... Label {key} is removed from namespace {namespace} ... ')
        except Exception as e:
            log(f'... Label {key} was not deleted! ... \nSome exception is occured: {e}')

    def get_cloud_apiversions(self):
        """
        Returns first element from list of available api versions in the cloud.
        Usually list contains one element.
        """
        response = (self.k8s_core_api.get_api_versions()).versions
        return response[0]

    def get_cloud_type(self):
        """
        Returns cloud type(openshift or kubernetes) of current environment via apiVersions list
        """
        try:
            apiVersionsList = (self.k8s_apis_api.get_api_versions()).groups
            for el in apiVersionsList:
                if el.name == 'route.openshift.io':
                    cloud_type = 'openshift'
                    break
                else:
                    cloud_type = 'kubernetes'
            return cloud_type
        except Exception as e:
            log(f'...  Unable to identify cloud type: {e}')

    def create_pod_security_policys_by_path(self, file_name):
        if isinstance(file_name, str):
            body = self.parse_yaml_from_file(file_name)
            self.create_pod_security_policy(body)
        elif isinstance(file_name, list):
            for file in file_name:
                body = self.parse_yaml_from_file(file)
                self.create_pod_security_policy(body)
        log('... All PSPs are created ...')

    def create_pod_security_policy(self, body):
        try:
            self.policy_v1beta1_api.create_pod_security_policy(body)
        except Exception as e:
            log(f"... PodSecurityPolicy {body.get('metadata').get('name')} cant be crated due: {e} ... ")

    def delete_psp_list(self, psp_names):
        """
        The function deletes PSP resources by specified names.
        `psp_names` parameter specify the list of PSP names should be deleted.
        """
        for psp in psp_names:
            self.delete_psp(psp)
        log('... All PSPs are deleted ...')

    def delete_psp(self, psp):
        """
        The function deletes PSP resource by specified name.
        """
        try:
            self.policy_v1beta1_api.delete_pod_security_policy(name=psp)
            log(f'... PSP {psp} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... PSP {psp} is not exist! ... ')
            else:
                log(f'... Psp {psp} is not deleted! \n{e}')

    def get_namespaced_deployment_configs(self, namespace: str):

        """
        Most useful for removing specific resources in OpenShift.
        Uses for get DeploymentConfig - resources that are
        not available in the Kubernetes.
        """

        deployment_configs = self.dyn_client.resources.get(
            api_version='apps.openshift.io/v1',
            kind='DeploymentConfig') \
            .get(namespace=namespace). \
            items
        deployments = []
        for deployment in deployment_configs:
            deployments.append(deployment.metadata.name)
        return deployments


    def _get_resource(self,
                      api_version: str,
                      kind: str,
                      label_selector: str = None,
                      namespace: str = None,
                      **kwargs) -> List[ResourceInstance]:
        """
        Most useful for removing specific resources in OpenShift.
        For example, delete Route, DeploymentConfig, SecurityContextConstraints - resources that are
        not available in the Kubernetes.
        """
        return self.dyn_client.resources.get(api_version=api_version, kind=kind) \
            .get(namespace=namespace, label_selector=label_selector) \
            .items

    def _delete_resource(self,
                         api_version: str,
                         kind: str,
                         name: str,
                         namespace: str = None,
                         **kwargs) -> List[ResourceInstance]:
        """
        Most useful for removing specific resources in OpenShift.
        For example, delete Route, DeploymentConfig, SecurityContextConstraints - resources that are
        not available in the Kubernetes.
        """
        return self.dyn_client.resources.get(api_version=api_version, kind=kind) \
            .delete(name=name, namespace=namespace)

    def _delete_scc(self,
                    name: str,
                    namespace: str = None,
                    **kwargs) -> List[ResourceInstance]:
        """
        The function deletes SecurityContextConstraints resources. Most useful for delete this resources
        in OpenShift. In Kubernetes the SecurityContextConstraints resources are not available.
        """
        api_version = 'security.openshift.io/v1'
        kind = 'SecurityContextConstraints'
        try:
            self.dyn_client.resources.get(api_version=api_version, kind=kind) \
                .delete(name=name, namespace=namespace)
            log(f'... SecurityContextConstraints {name} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Security Context Constraints {name} is not found! ... ')
            else:
                log(f'... Security Context Constraints {name} is not deleted!\n{e}')

    def delete_scc_by_name(self, names, namespace: str = None):
        """
        The function deletes a SecurityContextConstraints resource by specified name. Most useful for delete
        this resource in the OpenShift. In the Kubernetes SecurityContextConstraints resources are not available.
        `names` parameter can be passed as a list or string value.
        """
        if isinstance(names, str):
            self._delete_scc(name=names, namespace=namespace)
        elif isinstance(names, list):
            for name in names:
                self._delete_scc(name=name, namespace=namespace)

    def delete_scc_in_openshift(self, names, paas_platform: str):
        """
        The function deletes a SecurityContextConstraints resource by specified name only in Openshift. To specify
        cloud type set the following value to the parameter `paas_platform`: `openshift` or `kubernetes`.
        """
        log('... Used PAAS_PLATFORM: ' + paas_platform)
        paas_platform = paas_platform.lower()
        if paas_platform == 'kubernetes':
            return
        if paas_platform == 'openshift':
            self.delete_scc_by_name(names)
            return

    def get_all_scc(self) -> List[ResourceInstance]:
        """
        The function get all SecurityContextConstraints resources exists in the OpenShift. Most useful for
        executing in the OpenShift. In the Kubernetes SecurityContextConstraints resources are not available.
        """
        api_version = 'security.openshift.io/v1'
        kind = 'SecurityContextConstraints'
        return self._get_resource(api_version=api_version, kind=kind)

    def delete_namespace(self, name):
        """
        The function deletes the namespace by specified name.
        """
        try:
            self.k8s_core_v1_client.delete_namespace(name=name)
            log(f'... Namespace {name} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Namespace {name} is not found! ... ')
            else:
                log(f'... Namespace {name} is not deleted! \n{e}')

    def patch_pv(self, pv_list: list):
        """
        The function patch Persistent Volume in the cloud by specified PV list.
        """
        pv_body = [
            {
                'op': 'replace',
                'path': '/spec/claimRef',
                'value': None
            },
            {
                'op': 'replace',
                'path': '/status/phase',
                'value': 'Available'
            }
        ]
        for pv in pv_list:
            self.k8s_core_v1_client.patch_persistent_volume(pv, pv_body)
            log(f'... Persistent Volume {pv} is patched ... ')
        log(f'... All Persistent Volumes are patched ... ')


    def create_namespaced_role(self, body, namespace: str):
        """
        The function creates Role resource in the current namespace.
        """
        try:
            self.rbac_authorization.create_namespaced_role(namespace=namespace,
                                                           body=body,
                                                           pretty='true')
            log(f'... Role {body.get("metadata").get("name")} is created in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Some Exception is occured.\n{e}')

    def create_restricted_roles(self, list_namespaces: list):
        """
        The function creates Role resource in each namespace that includes in `list_namespaces` parameter.
        The function is only applicable for restricted deployment.
        """
        body = dict(
            apiVersion='rbac.authorization.k8s.io/v1',
            kind='Role',
            metadata=dict(
                name='restricted',
            ),
            rules=[dict(
                apiGroups=['*'],
                resources=['*'],
                verbs=['*'],
            )]
        )
        for namespace in list_namespaces:
            self.create_namespaced_role(namespace=namespace,
                                        body=body
                                        )

    def list_namespaced_role_binding_names(self, namespace):
        role_bindings = self.list_namespaced_role_binding(namespace)
        names = []
        for binding in role_bindings.items:
            names.append(binding.metadata.name)
        return names

    def create_namespaced_role_binding(self, body, namespace: str):
        """
        The function creates RoleBinding resource in current namespace.
        """
        try:
            self.rbac_authorization.create_namespaced_role_binding(namespace=namespace,
                                                                   body=body,
                                                                   pretty='true')
            log(f'... RoleBinding {body.get("metadata").get("name")} is created in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Some Exception is occured.\n{e}')

    def create_restricted_role_bindings(self, list_namespaces: list, restricted_sa_name: str = 'restricted'):
        """
        The function creates RoleBinding resource in each namespace that includes in `list_namespaces` parameter.
        The function is only applicable for restricted deployment.
        `restricted_sa_name` parameter specify name of restricted service account that should be used for
        restricted deployment.
        """
        body = dict(
            apiVersion='rbac.authorization.k8s.io/v1',
            kind='RoleBinding',
            metadata=dict(
                name='restricted',
            ),
            roleRef=dict(
                apiGroup='rbac.authorization.k8s.io',
                kind='Role',
                name='restricted'
            ),
            subjects=[dict(
                kind='ServiceAccount',
                name='restricted_sa_name',
                namespace='kube-system'
            )]
        )
        (body.get('subjects')[0]).update({'name': restricted_sa_name})

        for namespace in list_namespaces:
            self.create_namespaced_role_binding(namespace=namespace,
                                                body=body)

    def delete_namespaced_role_binding_by_name(self, name, namespace):
        """
        The function deletes RoleBinding resource in current namespace by specified name.
        """
        try:
            self.rbac_authorization.delete_namespaced_role_binding(name=name, namespace=namespace, pretty='true')
            log(f'... RoleBinding {name} is deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Cant delete RoleBinding {name} in {namespace}! \n{e}')

    def create_cluster_role(self, body):
        """
        The function creates Cluster Role resource in the cloud.
        """
        try:
            self.rbac_authorization.create_cluster_role(body=body, pretty='true')
            log(f'... ClusterRole {body.get("metadata").get("name")} is created! ... ')
        except Exception as e:
            log(f'... Some Exception is occured during creating cluster role {body}.\n{e}')

    def create_cluster_roles_by_path(self, array_files: list):
        """
        The function creates list of ClusterRoles resources in the cloud.
        `array_files` parameter specify the list of files paths that consist YAML templates.
        Files must be in the current repository.
        """
        for file_name in array_files:
            body = self.parse_yaml_from_file(file_name)
            self.create_cluster_role(body)
        log('... All ClusterRoles are created! ...')

    def create_cluster_role_binding(self, body):
        """
        The function creates ClusterRoleBinding resource in the cloud.
        """
        try:
            self.rbac_authorization.create_cluster_role_binding(body=body, pretty='true')
            log(f'... ClusterRoleBinding {body.get("metadata").get("name")} is created! ... ')
        except Exception as e:
            log(f'... Some Exception is occured.\n{e}')

    def create_cluster_role_bindings_by_path(self, array_files: list):
        """
        The function creates list of ClusterRoleBindings resources in the cloud.
        `array_files` parameter specify the list of files paths that consist YAML templates.
        Files must be in the current repository.
        """
        for file_name in array_files:
            body = self.parse_yaml_from_file(file_name)
            self.create_cluster_role_binding(body)
        log('... All ClusterRoleBindings are created ...')

    def delete_cluster_role(self, name: str):
        """
        The function deletes Cluster Role resource by specified name.
        """
        try:
            self.rbac_authorization.delete_cluster_role(name=name)
            log(f'... Cluster Role {name} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Cluster Role {name} is not exist! ... ')
            else:
                log(f'... Cluster Role {name} is not deleted! \n{e}')

    def delete_cluster_roles(self, array_names: list):
        """
        The function deletes Cluster Roles resources by specified names.
        `array_names` parameter specify the list of role names should be deleted.
        """
        for role_name in array_names:
            self.delete_cluster_role(role_name)
        log('... All ClusterRoles are deleted ...')

    def delete_cluster_role_binding(self, name):
        """
        The function deletes Cluster Role Binding resource by specified name.
        """
        try:
            self.rbac_authorization.delete_cluster_role_binding(name=name)
            log(f'... Cluster RoleBinding {name} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Cluster RoleBinding {name} is not exist! ... ')
            else:
                log(f'... Cluster RoleBinding {name} is not deleted! \n{e}')

    def delete_cluster_role_bindings(self, array_names: list):
        """
        The function deletes Cluster Role Bindings resources by specified names.
        `array_names` parameter specify the list of role binding names should be deleted.
        """
        for file_name in array_names:
            self.delete_cluster_role_binding(file_name)
        log('... All ClusterRoleBindings are deleted ...')

    def delete_namespaced_custom_object(self, group, version, namespace, plural, name):
        """Delete existing custom object resource (CR) by provided group, api version, plural, name
        in the namespace.

        :param group: the custom resource's group name
        :param version: the custom resource's version
        :param namespace: the custom resource's namespace
        :param plural: the custom resource's plural name. For TPRs this would be lowercase plural kind.
        :param name: the name of custom object to delete.

        Example:
        delete_namespaced_custom_object(integreatly.org, v1alpha1, vault-namespace, grafanadashboards, dashboard_vault)
        """
        try:
            self.custom_objects_api.delete_namespaced_custom_object(group=group, version=version,
                                                                    namespace=namespace, plural=plural,
                                                                    name=name, pretty='true')
            log(f'... Custom Resource is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Custom Resource is not exist! ... ')
            else:
                log(f'... Custom Resource is not deleted! \n{e}')

    def delete_namespaced_custom_object_with_deleting_finilaizer(self, group, version, namespace, plural, name):
        try:
            cr = self.custom_objects_api.get_namespaced_custom_object(group, version, namespace, plural, name)
            if cr['metadata'].get('finalizers'):
                cr['metadata']['finalizers'] = []
                self.custom_objects_api.replace_namespaced_custom_object(group, version, namespace, plural, name, cr)
                self.custom_objects_api.delete_namespaced_custom_object(group, version, namespace, plural, name, grace_period_seconds=0)
                log(f'... Custom Resource is patched for delete finilaizers and after that deleted! ... ')
            else:
                print(f'No finalizers in CR: {name}, NS: {namespace}')
        except Exception as e:
            if e.status == 404:
                log(f'... Custom Resource is not exist! ... ')
            else:
                log(f'... Custom Resource is not deleted! \n{e}')

    def delete_dashboard_in_namespace(self, namespace, name):
        """Deletes resource 'GrafanaDashboard' custom object in project/namespace.

        :param namespace: namespace of existing GrafanaDashboard
        :param name: the name of GrafanaDashboard to delete
        """
        return self.delete_namespaced_custom_object(group='integreatly.org', version='v1alpha1',
                                                    namespace=namespace, plural='grafanadashboards',
                                                    name=name)

    def get_custom_resource_definition(self, name, version: str):
        group = 'apiextensions.k8s.io'
        plural = 'customresourcedefinitions'
        try:
            body = self.custom_objects_api.get_cluster_custom_object(group, version, plural, name)
            return body
        except Exception as e:
            return False

    def create_custom_resource_definition(self, body, version: str):
        """
        The function creates Custom Resource Definition (CRD) resource.
        `version` parameter specify actual apiversion of resource in cloud. List of actual api version
        that available in cloud can get via function `get_cloud_apiversions`.
        """
        group = 'apiextensions.k8s.io'
        plural = 'customresourcedefinitions'
        try:
            self.custom_objects_api.create_cluster_custom_object(group, version,
                                                                 plural, body,
                                                                 pretty='true')
            log(f'... Custom Resource Definition {body.get("metadata").get("name")} is created! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not exist! ... ')
            else:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not created! \n{e}')

    def create_custom_resource_definitions_by_path(self, array_files: list):
        """
        The function creates list of Custom Resource Definitions (CRDs) resources.
        `array_files` parameter specify the list of files paths that consist yaml templates.
        Files must be in the current repository.
        """
        for file_name in array_files:
            body = self.parse_yaml_from_file(file_name)
            version = 'v1'
            self.create_custom_resource_definition(body=body, version=version)
        log('... All Custom Resource Definitions are created ...')

    def replace_custom_resource_definition(self, name, body):
        try:
            self.k8s_api_ext_v1_client.replace_custom_resource_definition(name, body)
            log(f'... Custom Resource Definition {body.get("metadata").get("name")} is replaced! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not exist! ... ')
            else:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not replaced! \n{e}')

    def patch_custom_resource_definition(self, name, body):
        try:
            self.k8s_api_ext_v1_client.patch_custom_resource_definition(name, body)
            log(f'... Custom Resource Definition {body.get("metadata").get("name")} is patched! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not exist! ... ')
            else:
                log(f'... Custom Resource Definition {body.get("metadata").get("name")} is not patched! \n{e}')

    def create_security_context_constraints(self, body, version: str):
        """
        The function creates SCC resource.
        `version` parameter specify actual apiversion of resource in cloud. List of actual api version
        that available in cloud can get via function `get_cloud_apiversions`.
        """
        group = 'security.openshift.io'
        plural = 'securitycontextconstraints'
        try:
            self.custom_objects_api.create_cluster_custom_object(group, version,
                                                                 plural, body,
                                                                 pretty='true')
            log(f'... SCC {body.get("metadata").get("name")} is created! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... SCC {body.get("metadata").get("name")} is not exist! ... ')
            else:
                log(f'... SCC {body.get("metadata").get("name")} is not created! \n{e}')

    def create_security_context_constraints_by_path(self, array_files: list):
        """
        The function creates list of SCCs resources.
        `array_files` parameter specify the list of files paths that consist yaml templates.
        Files must be in the current repository.
        """
        for file_name in array_files:
            body = self.parse_yaml_from_file(file_name)
            version = 'v1'
            self.create_security_context_constraints(body=body, version=version)
        log('... All SCC are created ...')

    def delete_custom_resource_definition(self, name: str, version: str):
        """
        The function deletes Custom Resource Definition (CRDs) by specified name and version.
        `version` parameter specify the api version of CRD. List of actual api version that available
         in cloud can get via function `get_cloud_apiversions`.

        Example:
        delete_custom_resource_definition('loggingservices.qubership.org','v1')
        """
        group = 'apiextensions.k8s.io'
        plural = 'customresourcedefinitions'
        try:
            self.custom_objects_api.delete_cluster_custom_object(group=group, version=version,
                                                                 plural=plural, name=name)
            log(f'... Request for deletion  {name} sent successfully ...')
        except Exception as e:
            if e.status == 404:
                log(f'Custom Resource Definition {name} is not exist!')
            else:
                log(f'Custom Resource Definition {name} cant be deleted!\n{e}')

    def delete_crd_with_undefine_version(self, name: str, with_check=False):
        """
        The function deletes Custom Resource Definition (CRDs) by specified name.

        Example:
        delete_crd_with_undefine_version('loggingservices.qubership.org')
        """
        version = self.get_cloud_apiversions()
        try:
            self.delete_custom_resource_definition(name=name, version=version)
            time.sleep(5)
            if with_check:
                crd_body = self.get_custom_resource_definition(name=name, version=version)
                finalizers = crd_body['metadata'].get('finalizers')
                if finalizers:
                    crd_body['metadata']['finalizers'] = []
                    self.patch_custom_resource_definition(name, crd_body)
                for i in range(10):
                    crd_body = self.get_custom_resource_definition(name=name, version=version)
                    if crd_body:
                        time.sleep(5)
                    else:
                        log(f'Custom Resource Definition {name} is deleted!\n')
                        break
        except Exception as e:
            if with_check:
                log(f'Custom Resource Definition {name} is deleted!\n{e}')
            else:
                log(f'Custom Resource Definition {name} is not deleted!\n{e}')

    def delete_finalizer(self, obj_type, namespace):
        if obj_type == "stateful_set":
            list = self.k8s_apps_v1_client.list_namespaced_stateful_set
            replace = self.k8s_apps_v1_client.replace_namespaced_stateful_set
        elif obj_type == "deployment":
            list = self.k8s_apps_v1_client.list_namespaced_deployment
            replace = self.k8s_apps_v1_client.replace_namespaced_deployment
        elif obj_type == "config_map":
            list = self.k8s_core_v1_client.list_namespaced_config_map
            replace = self.k8s_core_v1_client.replace_namespaced_config_map
        elif obj_type == "secret":
            list = self.k8s_core_v1_client.list_namespaced_secret
            replace = self.k8s_core_v1_client.replace_namespaced_secret
        elif obj_type == "service":
            list = self.k8s_core_v1_client.list_namespaced_service
            replace = self.k8s_core_v1_client.replace_namespaced_service
        elif obj_type == "service_account":
            list = self.k8s_core_v1_client.list_namespaced_service_account
            replace = self.k8s_core_v1_client.replace_namespaced_service_account
        elif obj_type == "role":
            list = self.rbac_authorization.list_namespaced_role
            replace = self.rbac_authorization.replace_namespaced_role
        elif obj_type == "role_binding":
            list = self.rbac_authorization.list_namespaced_role_binding
            replace = self.rbac_authorization.replace_namespaced_role_binding
        elif obj_type == "persistent_volume_claim":
            list = self.k8s_core_v1_client.list_namespaced_persistent_volume_claim
            replace = self.k8s_core_v1_client.replace_namespaced_persistent_volume_claim
        else: log(f'... Can not delete the finalizer from an object {obj_type} ...')
        objects = list(namespace)
        for object in objects.items:
            metadata = object.metadata.to_dict()
            name = metadata.get("name")
            finalizers = metadata.get("finalizers")
            log(f'Start work with {obj_type}, name: {name} and finalizers: {finalizers} ...')
            if finalizers != None:
                log(f'..... Update {obj_type}, name: {name} and finalizers: {finalizers} ...')
                object.metadata.finalizers = None
                replace(name, namespace, object)
                log(f'..... Finalizers are deleted from resource {obj_type}, name: {name}')


    def delete_finalizer_in_cr(self, group, version, namespace, plural):
        crs = self.custom_objects_api.list_namespaced_custom_object(group=group,
                                                                           version=version,
                                                                           namespace=namespace,
                                                                           plural=plural)
        crs_items = crs.get("items")
        for cr in crs_items:
            metadata = cr.get("metadata")
            finalizers = metadata.get("finalizers")
            name = metadata.get("name")
            if finalizers != None:
                cr["metadata"]["finalizers"] = None
                self.custom_objects_api.replace_namespaced_custom_object(group, version, namespace, plural, name, cr)

    def delete_collection_namespaced_role(self, namespace):
        """
        The function deletes all Roles resources existing in the namespace.
        """
        try:
            self.rbac_authorization.delete_collection_namespaced_role(namespace=namespace,
                                                                      pretty='true',
                                                                      grace_period_seconds=0)
            self.delete_finalizer("role", namespace)
            log(f'... All existing Roles are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Roles in {namespace}! \n{e}')

    def delete_collection_namespaced_role_binding(self, namespace):
        """
        The function deletes all Role Bindings resources existing in the namespace.
        """
        try:
            self.rbac_authorization.delete_collection_namespaced_role_binding(namespace=namespace,
                                                                              pretty='true',
                                                                              grace_period_seconds=0)
            self.delete_finalizer("role_binding", namespace)
            log(f'... All existing Role Bindings are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Role Bindings in {namespace}! \n{e}')

    def delete_collection_namespaced_deployment(self, namespace: str):
        """
        The function deletes all Deployments resources existing in the namespace.
        """
        try:
            self.k8s_apps_v1_client.delete_collection_namespaced_deployment(namespace=namespace,
                                                                            pretty='true',
                                                                            grace_period_seconds=0)
            self.delete_finalizer("deployment", namespace)
            log(f'... All existing Deployments are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Deployments in {namespace}! \n{e}')

    def delete_collection_namespaced_deployment_configs(self, namespace: str):
        """
        The function deletes all Deployment configs resources existing in the namespace.
        """
        try:
            deployments = self.get_namespaced_deployment_configs(namespace)
            log(f'... Following deployment configs will be deleted: {deployments}! ... ')
            for deployment in deployments:
                self._delete_resource(api_version='apps.openshift.io/v1', kind='DeploymentConfig', name=deployment, namespace=namespace)
            log(f'... All existing Deployment configs are deleted in namespace {namespace}! ...\n')
        except Exception as e:
            log(f'... Can not delete Deployment configs in {namespace}! \n{e}')

    def delete_collection_namespaced_replica_set(self, namespace: str):
        """
        The function deletes all Replica Set resources existing in the namespace.
        """
        try:
            self.k8s_apps_v1_client.delete_collection_namespaced_replica_set(namespace=namespace,
                                                                             pretty='true',
                                                                             grace_period_seconds=0)
            log(f'... All existing Replica Sets are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Replica Sets in {namespace}! \n{e}')



    def delete_collection_namespaced_event(self, namespace: str):
        """
        The function deletes all Events resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_event(namespace=namespace,
                                                                       pretty='true',
                                                                       grace_period_seconds=0)
            log(f'... All existing Events are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Events in {namespace}! \n{e}')

    def delete_collection_namespaced_ingress(self, namespace: str):
        """
        The function deletes all Ingress resources existing in the namespace.
        """
        try:
            self.net_v1_api.delete_collection_namespaced_ingress(namespace=namespace,
                                                                 pretty='true',
                                                                 grace_period_seconds=0)
            log(f'... All existing Ingress are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Ingress in {namespace}! \n{e}')

    def delete_collection_namespaced_config_map(self, namespace: str):
        """
        The function deletes all Config Maps resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_config_map(namespace=namespace,
                                                                            pretty='true',
                                                                            grace_period_seconds=0)
            self.delete_finalizer("config_map", namespace)
            log(f'... All existing Config Maps are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Config Maps in {namespace}! \n{e}')

    def delete_collection_namespaced_secret(self, namespace: str):
        """
        The function deletes all Secrets resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_secret(namespace=namespace,
                                                                        pretty='true',
                                                                        grace_period_seconds=0)
            self.delete_finalizer("secret", namespace)
            log(f'... All existing Secrets are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Secrets in {namespace}! \n{e}')

    def list_namespaced_service_account(self, namespace):
        return self.k8s_core_v1_client.list_namespaced_service_account(namespace=namespace)

    def delete_namespaced_service_account(self, name, namespace):
        self.k8s_core_v1_client.delete_namespaced_service_account(name, namespace)

    def list_namespaced_service_account_names(self, namespace):
        service_accounts = self.list_namespaced_service_account(namespace)
        names = []
        for sa in service_accounts.items:
            names.append(sa.metadata.name)
        return names

    def delete_collection_namespaced_service_account(self, namespace: str):
        """
        The function deletes all Service Accounts resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_service_account(namespace=namespace,
                                                                                 pretty='true',
                                                                                 grace_period_seconds=0)
            self.delete_finalizer("service_account", namespace)
            log(f'... All existing Service Accounts are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Service Accounts in {namespace}! \n{e}')

    def delete_collection_namespaced_pod(self, namespace: str):
        """
        The function deletes all Pods resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_pod(namespace=namespace,
                                                                     pretty='true',
                                                                     grace_period_seconds=0)
            log(f'... All existing Pods are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Pods in {namespace}! \n{e}')

    def delete_collection_namespaced_stateful_set(self, namespace: str):
        """
        The function deletes all Stateful Set resources existing in the namespace.
        """
        try:
            self.k8s_apps_v1_client.delete_collection_namespaced_stateful_set(namespace=namespace,
                                                                              pretty='true',
                                                                              grace_period_seconds=0)
            self.delete_finalizer("stateful_set", namespace)
            log(f'... All existing Stateful Sets are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Stateful Sets in {namespace}! \n{e}')

    def delete_collection_namespaced_persistent_volume_claim(self, namespace: str):
        """
        The function deletes all Persistent Volumes resources existing in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_persistent_volume_claim(namespace=namespace,
                                                                                         pretty='true',
                                                                                         grace_period_seconds=0)
            self.delete_finalizer("persistent_volume_claim", namespace)
            log(f'... All existing Persistent Volumes are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Persistent Volumes in {namespace}! \n{e}')

    def create_namespaced_service(self, body, namespace: str):
        """
        The function creates Service resource in the namespace by specified body.
        """
        try:
            self.k8s_core_v1_client.create_namespaced_service(body=body, namespace=namespace,
                                                              pretty='true')
            log(f'... Service is created in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not create Service in {namespace}! \n{e}')


    def delete_namespaced_role(self, name: str, namespace: str):
        """
        The function deletes Role resource in the current namespace by specified name.
        """
        try:
            self.rbac_authorization.delete_namespaced_role(name=name,
                                                           namespace=namespace,
                                                           pretty='true')
            log(f'... Role {name} is deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Role {name} in {namespace}! \n{e}')
    
    def delete_security_context_constraints(self, name, version: str):
        """
        The function deletes SCC resource.
        `version` parameter specify actual apiversion of resource in cloud. List of actual api version
        that available in cloud can get via function `get_cloud_apiversions`.
        """
        group = 'security.openshift.io'
        plural = 'securitycontextconstraints'
        try:
            self.custom_objects_api.delete_cluster_custom_object(group=group, version=version,
                                                                 plural=plural, name=name)
            log(f'... SCC {name} is deleted! ... ')
        except Exception as e:
            if e.status == 404:
                log(f'... SCC {name} doesnt exist! ... ')
            else:
                log(f'... SCC {name} cant be deleted! \n{e}')

    def delete_namespaced_service(self, name: str, namespace: str):
        """
        The function deletes Service resource existing in the namespace by specified name.
        """
        try:
            self.k8s_core_v1_client.delete_namespaced_service(name=name, namespace=namespace,
                                                              pretty='true')
            log(f'... Service {name} is deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Service {name} in {namespace}! \n{e}')

    def delete_collection_namespaced_service(self, namespace: str):
        """
        The function deletes all Services resources existing in the namespace.
        """
        namespaced_services = self.k8s_core_v1_client.list_namespaced_service(namespace).items
        for service in namespaced_services:
            self.delete_namespaced_service(service.metadata.name, namespace)
        self.delete_finalizer("service", namespace)
        log(f'... All existing Services are deleted in {namespace}!')

    def delete_collection_namespaced_daemon_set(self, namespace: str):
        """
        The function deletes all existing Daemon Set resources in the namespace.
        """
        try:
            self.k8s_apps_v1_client.delete_collection_namespaced_daemon_set(namespace=namespace, pretty='true', grace_period_seconds=0)
            log(f'... All existing Daemon Sets are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Daemon Sets in {namespace}! \n{e}')

    def delete_collection_namespaced_custom_object(self, group, version, namespace, plural):
        """
        The function deletes all existing Custom Object resource (CR) by provided group, api version, plural
        in the namespace.

        :param group: the custom resource's group name
        :param version: the custom resource's version
        :param namespace: the custom resource's namespace
        :param plural: the custom resource's plural name. For TPRs this would be lowercase plural kind.

        Example:
        delete_collection_namespaced_custom_object(integreatly.org, v1alpha1, vault-namespace, grafanadashboards)
        """

        try:
            self.custom_objects_api.delete_collection_namespaced_custom_object(group=group, version=version,
                                                                               namespace=namespace, plural=plural,
                                                                               pretty='true')
            self.delete_finalizer_in_cr(group, version, namespace, plural)
            log(f'... All existing Custom Resources are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Custom Resources in {namespace}! \n{e}')

    def delete_collection_namespaced_dashboards(self, namespace):
        """
        The function deletes all existing Dashboards resources (CR) in the namespace.
        """
        try:
            self.delete_collection_namespaced_custom_object(group='integreatly.org', version='v1alpha1',
                                                            namespace=namespace, plural='grafanadashboards')
            log(f'... All existing Dashboards are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Dashboards in {namespace}! \n{e}')

    def delete_collection_namespaced_service_monitors(self, namespace):
        """
        The function deletes all existing Service Monitor resources (CR) in the namespace.
        """
        try:
            self.delete_collection_namespaced_custom_object(group='monitoring.coreos.com', version='v1',
                                                              namespace=namespace, plural='servicemonitors')
            log(f'... All existing Service Monitors are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Service Monitors in {namespace}! \n{e}')

    def delete_collection_namespaced_prometheus_rules(self, namespace):
        """
        The function deletes all existing Prometheus Rule resources (CR) in the namespace.
        """
        try:
            self.delete_collection_namespaced_custom_object(group='monitoring.coreos.com', version='v1',
                                                              namespace=namespace, plural='prometheusrules')
            log(f'... All existing Prometheus Rules are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Prometheus Rules in {namespace}! \n{e}')

    def delete_collection_namespaced_replication_controller(self, namespace):
        """
        The function deletes all existing Replication Controllers in the namespace.
        """
        try:
            self.k8s_core_v1_client.delete_collection_namespaced_replication_controller(namespace=namespace,
                                                                     pretty='true',
                                                                     grace_period_seconds=0)
            log(f'... All existing Replication Controllers are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Replication Controllers in {namespace}! \n{e}')

    def delete_collection_namespaced_pod_monitors(self, namespace):
        """
        The function deletes all existing Pod Monitors in the namespace.
        """
        try:
            self.delete_collection_namespaced_custom_object(group='monitoring.coreos.com', version='v1',
                                                              namespace=namespace, plural='podmonitors')
            log(f'... All existing Pod Monitors are deleted in namespace {namespace}! ... ')
        except Exception as e:
            log(f'... Can not delete Pod Monitors in {namespace}! \n{e}')

    def delete_api_service(self, api_service_name):
        """
        The function deletes Api Service by specified name
        """
        try:
            self.api_registration.delete_api_service(api_service_name)
            log(f'... Api Service {api_service_name} is deleted! ... ')
        except Exception as e:
            log(f'... Can not delete Api Service {api_service_name}! \n{e}')

    def create_api_service(self, body):
        """
        The function creates Api Service from yaml
        """
        try:
            self.api_registration.create_api_service(body)
            log(f"... Api Service {body.get('metadata').get('name')} is created! ... ")
        except Exception as e:
            log(f"... Can not create Api Service {body.get('metadata').get('name')}! \n{e}")

    def list_namespaced_role_binding(self, namespace):
        return self.rbac_authorization.list_namespaced_role_binding(namespace=namespace)

    def execute_command_in_pod(self, name: str, namespace: str, command: str, container: str = "", shell: str = "/bin/bash"):
        """Executes given console command within docker container.
        `container` variable specifies name of container. It can be empty if pod contains only one container.
        The Pod is found by name and project/namespace. Method executes given console command within the stream and
        returns tuple of command result and error message (all of them can be empty).
        """
        exec_cmd = [shell, '-c', command]
        response = stream(self.k8s_core_v1_client.connect_get_namespaced_pod_exec,
                          name,
                          namespace,
                          container=container,
                          command=exec_cmd,
                          stderr=True,
                          stdin=False,
                          stdout=True,
                          tty=False,
                          _preload_content=False,
                          _request_timeout=60)

        result = ""
        errors = ""
        while response.is_open():
            response.update(timeout=60)
            if response.peek_stdout():
                value = str(response.read_stdout())
                result += value
            if response.peek_stderr():
                error = response.read_stderr()
                errors += error
        return result.strip(), errors.strip()

    def list_namespaced_pod(self, namespace):
        return self.k8s_core_v1_client.list_namespaced_pod(namespace)

    def list_namespaced_secret_names(self, namespace: str):
        secrets = []
        namespaced_secrets = self.k8s_core_v1_client.list_namespaced_secret(namespace).items
        for secret in namespaced_secrets:
            secrets.append(secret.metadata.name)
        return secrets

    def read_namespaced_secret(self, name, namespace):
        return self.k8s_core_v1_client.read_namespaced_secret(name, namespace)

    def replace_namespaced_secret(self, name, namespace, body):
        self.k8s_core_v1_client.replace_namespaced_secret(name, namespace, body)
        print(f'Secret: {name} replaced!')

    def patch_namespaced_secret(self, name, namespace, body):
        self.k8s_core_v1_client.patch_namespaced_secret(name, namespace, body)
        print(f'Secret: {name} patched!')

    def read_namespaced_pod_log(self, pod_name, namespace, container):
        return self.k8s_core_v1_client.read_namespaced_pod_log(pod_name, namespace, container=container, pretty=True, timestamps=True)

    def list_nodes(self):
        return self.k8s_core_v1_client.list_node()

    def read_node_status(self, name):
        return self.k8s_core_v1_client.read_node_status(name)

    def get_deployment_entities_count_for_service(self, namespace: str, service: str, label: str ='clusterName'):
        return len(self.get_deployment_entity_names_for_service(namespace, service, label))

    def get_deployment_entity_names_for_service(self, namespace: str, service: str, label: str ='clusterName') -> list:
        deployments = self.get_deployment_entities(namespace)
        return [deployment.metadata.name for deployment in deployments
                if deployment.spec.template.metadata.labels.get(label, '') == service]

    def get_deployment_entities(self, namespace: str) -> list:
        return [deployment for deployment in self.k8s_apps_v1_client.list_namespaced_deployment(namespace).items]

    def get_active_deployment_entities_count_for_service(self,
                                                         namespace: str,
                                                         service: str,
                                                         label: str ='clusterName') -> int:
        return len(self.get_active_deployment_entities_for_service(namespace, service, label))

    def get_active_deployment_entities_for_service(self,
                                                   namespace: str,
                                                   service: str,
                                                   label: str ='clusterName') -> list:
        deployments = self.get_deployment_entities(namespace)
        active_deployments = []

        for deployment in deployments:
            if deployment.spec.template.metadata.labels.get(label, '') == service \
                    and not deployment.status.unavailable_replicas \
                    and deployment.status.available_replicas is not None:
                active_deployments.append(deployment)
        return active_deployments

    def delete_collection_namespaced_secret_exclude_helm_based(self, namespace):
        list_secrets = self.k8s_core_v1_client.list_namespaced_secret(namespace)
        for secret in list_secrets.items:
            if "sh.helm.release" not in secret.metadata.name:
                try:
                    self.k8s_core_v1_client.delete_namespaced_secret(name=secret.metadata.name, namespace=namespace, body=client.V1DeleteOptions())
                    print(f'Secret {secret.metadata.name} is deleted')
                except:
                    print(f'Secret {secret.metadata.name} is not deleted')
            else:
                print(f'Secret {secret.metadata.name} is helm related, not be deleted')


    def delete_collection_namespaced_role_with_excluding(self, namespace, excluding_roles):
        list_roles = self.rbac_authorization.list_namespaced_role(namespace)
        for role in list_roles.items:
            if role.metadata.name not in excluding_roles:
                try:
                    self.rbac_authorization.delete_namespaced_role(name=role.metadata.name, namespace=namespace)
                    print(f'Role {role.metadata.name} is deleted')
                except:
                    print(f'Role {role.metadata.name} is not deleted')
            else:
                print(f'Role {role.metadata.name} is excluded, not be deleted')

    def delete_collection_namespaced_role_binding_with_excluding(self, namespace, excluding_role_bindings):
        list_role_bindings = self.rbac_authorization.list_namespaced_role_binding(namespace)
        for role_binding in list_role_bindings.items:
            if role_binding.metadata.name not in excluding_role_bindings:
                try:
                    self.rbac_authorization.delete_namespaced_role_binding(name=role_binding.metadata.name, namespace=namespace)
                    print(f'Role binding {role_binding.metadata.name} is deleted')
                except:
                    print(f'Role binding {role_binding.metadata.name} is not deleted')
            else:
                print(f'Role binding {role_binding.metadata.name} is excluded, not be deleted')
