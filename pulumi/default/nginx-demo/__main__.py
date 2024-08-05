from lib.generate_kustomize import DeploymentJob, ServiceJob, ServiceAccountJob
import os

if __name__ == '__main__':
     app_config_path = os.getenv('APP_CONFIG_PATH')
     if not app_config_path:
         raise ValueError('APP_CONFIG_PATH environment variable is not set')
     else:
    
         # Create a DeploymentJob instance
         deployment_job = DeploymentJob(app_config_path)
         
         # Deploy the job
         deployment_job.deploy_job()
         
         # Create a ServiceJob instance and deploy the service
         service_job = ServiceJob(app_config_path)
         service_job.deploy_service()
         
         # Create a ServiceAccountJob instance and deploy the service account
         service_account_job = ServiceAccountJob(app_config_path)
         service_account_job.deploy_service_account()