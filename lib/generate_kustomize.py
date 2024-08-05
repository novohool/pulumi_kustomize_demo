import pulumi
import pulumi_vault as vault
import pulumi_kubernetes as k8s
import pulumi_kubernetes.kustomize as kustomize
import json
from jinja2 import Template
import os
import logging

class Provider:
    _instance = None

    @staticmethod
    def get_provider():
        if Provider._instance is None:
            config = pulumi.Config()
            vault_address = config.require("vault_address")
            vault_token = config.require_secret("vault_token")
            Provider._instance = vault.Provider(
                "vault-provider",
                address=vault_address,
                token=vault_token
            )
        return Provider._instance

class KustomizeFileGenerator:
    def __init__(self, pulumi_workspace):
        self.pulumi_workspace = pulumi_workspace

    def generate_file(self, template_path, output_path, context):
        with open(template_path) as f:
            template = Template(f.read())
        rendered = template.render(context)
        with open(output_path, 'w') as f:
            f.write(rendered)

    def generate_kustomize_files(self, context, app_namespace, app_name, template_name):
        kustomize_base_dir = f"{self.pulumi_workspace}/kustomize/{app_namespace}/{app_name}"
        os.makedirs(kustomize_base_dir, exist_ok=True)
        template_path = f"{self.pulumi_workspace}/templates/{template_name}.yaml"
        output_path = f"{kustomize_base_dir}/{template_name}/{template_name}.yaml"
        self.generate_file(template_path, output_path, context)

class DeploymentJob:
    def __init__(self, path):
        self.path = path
        self.provider = Provider.get_provider()
        self.config_secret = vault.generic.get_secret(
            path=path, 
            opts=pulumi.InvokeOptions(provider=self.provider)
        )
        self.app_name = self.config_secret.data["app_name"]
        self.app_namespace = self.config_secret.data["app_namespace"]
        self.replicas = int(self.config_secret.data["replicas"])
        self.image = self.config_secret.data["image"]
        self.labels = json.loads(self.config_secret.data["labels"])
        self.ports = json.loads(str(self.config_secret.data["ports"]))
        self.readiness_probe = json.loads(self.config_secret.data["readiness_probe"])
        self.init_containers = json.loads(str(self.config_secret.data["init_containers"]))
        self.commands = json.loads(self.config_secret.data["commands"])
        self.node_selector = json.loads(self.config_secret.data["node_selector"])
        self.resources = json.loads(self.config_secret.data["resources"])
        self.pulumi_workspace = os.getenv('PULUMI_WORKSPACE', "/app")
        self.kustomize_file_generator = KustomizeFileGenerator(self.pulumi_workspace)

    def deploy_job(self):
        # Generate dynamic configuration files
        context = {
            "app_name": self.app_name,
            "app_namespace": self.app_namespace,
            "replicas": self.replicas,
            "image": self.image,
            "labels": self.labels,
            "ports": self.ports,
            "readiness_probe": self.readiness_probe,
            "init_containers": self.init_containers,
            "commands": self.commands,
            "node_selector": self.node_selector,
            "resources": self.resources
        }
        self.kustomize_file_generator.generate_kustomize_files(context, self.app_namespace, self.app_name, "deployment")

        # Define the Kustomize directory
        kustomize_dir = f"{self.pulumi_workspace}/kustomize/{self.app_namespace}/{self.app_name}/deployment"

        # Use kustomize to create a resource
        deployment_kustomize_resource = kustomize.Directory(
            f"{self.app_namespace}_{self.app_name}_deployment_kustomize_resource",
            directory=kustomize_dir,
        )

        # Export the names of the resources
        pulumi.export(f"{self.app_namespace}_{self.app_name}_deployment_kustomize_resource", deployment_kustomize_resource.resources)

class ServiceJob:
    def __init__(self, path):
        self.path = path
        self.provider = Provider.get_provider()
        self.config_secret = vault.generic.get_secret(
            path=path, 
            opts=pulumi.InvokeOptions(provider=self.provider)
        )
        self.app_name = self.config_secret.data["app_name"]
        self.app_namespace = self.config_secret.data["app_namespace"]
        self.ports = self.config_secret.data["ports"]
        self.labels = json.loads(self.config_secret.data["labels"])
        self.pulumi_workspace = os.getenv('PULUMI_WORKSPACE', "/app")
        self.kustomize_file_generator = KustomizeFileGenerator(self.pulumi_workspace)

    def deploy_service(self):
        context = {
            "app_name": self.app_name,
            "app_namespace": self.app_namespace,
            "ports": json.loads(str(self.ports)),
            "labels": self.labels,
        }
        self.kustomize_file_generator.generate_kustomize_files(context, self.app_namespace, self.app_name, "service")

        # Define the Kustomize directory
        kustomize_dir = f"{self.pulumi_workspace}/kustomize/{self.app_namespace}/{self.app_name}/service"

        # Use kustomize to create a resource
        service_kustomize_resource = kustomize.Directory(
            f"{self.app_namespace}_{self.app_name}_service_kustomize_resource",
            directory=kustomize_dir,
        )

        # Export the names of the resources
        pulumi.export(f"{self.app_namespace}_{self.app_name}_service_kustomize_resource", service_kustomize_resource.resources)

class ServiceAccountJob:
    def __init__(self, path):
        self.path = path
        self.provider = Provider.get_provider()
        self.config_secret = vault.generic.get_secret(
            path=path, 
            opts=pulumi.InvokeOptions(provider=self.provider)
        )
        self.app_name = self.config_secret.data["app_name"]
        self.app_namespace = self.config_secret.data["app_namespace"]
        self.labels = json.loads(self.config_secret.data["labels"])
        self.pulumi_workspace = os.getenv('PULUMI_WORKSPACE', "/app")
        self.kustomize_file_generator = KustomizeFileGenerator(self.pulumi_workspace)

    def deploy_service_account(self):
        context = {
            "app_name": self.app_name,
            "app_namespace": self.app_namespace,
            "labels": self.labels,
        }
        self.kustomize_file_generator.generate_kustomize_files(context, self.app_namespace, self.app_name, "serviceaccount")

        # Define the Kustomize directory
        kustomize_dir = f"{self.pulumi_workspace}/kustomize/{self.app_namespace}/{self.app_name}/serviceaccount"

        # Use kustomize to create a resource
        serviceaccount_kustomize_resource = kustomize.Directory(
            f"{self.app_namespace}_{self.app_name}_serviceaccount_kustomize_resource",
            directory=kustomize_dir,
        )

        # Export the names of the resources
        pulumi.export(f"{self.app_namespace}_{self.app_name}_serviceaccount_kustomize_resource", serviceaccount_kustomize_resource.resources)