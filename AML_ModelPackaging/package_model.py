import argparse
import os

import pandas as pd
import mlflow
from mlflow import pyfunc
import subprocess

from azureml.core import Workspace, Model

def main():

    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--model_version",
        type=str,
        help="Name of a file to write model ID to"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of model"
    )
    args = parser.parse_args()
    model_name = args.model_name
    model_version = args.model_version
    print(args.model_name)
    print(model_version)
    
    ws = Workspace(subscription_id=os.getenv('SUBSCRIPTION_ID'), resource_group=os.getenv('RESOURCE_GROUP'), workspace_name=os.getenv('WORKSPACE_NAME'))

    mlflow.set_tracking_uri(ws.get_mlflow_tracking_uri())
    
    model = Model(ws, model_name, version=model_version)
    model_version = model.version
    model_uri = model.properties['mlflow.modelSourceUri']
    scaler_uri = model_uri.replace('/model','/scaler.pkl')
    threshold_uri  = model_uri.replace('/model','/threshold.txt')
    print(model)

    model.download('./deployment', exist_ok=True)
    mlflow.artifacts.download_artifacts(scaler_uri, dst_path='./deployment')
    mlflow.artifacts.download_artifacts(threshold_uri, dst_path='./deployment')

    from azureml.core import Environment
    from azureml.core.model import InferenceConfig

    env = Environment.from_dockerfile('TF_Autoencoder_Edge_Env', './Dockerfile')
    env.register(ws)
    inference_config = InferenceConfig(
        environment=env,
        source_directory="./deployment",
        entry_script="./score.py",
    )

    package = Model.package(ws, [model], inference_config, image_name=model_name, image_label=model_version)
    package.wait_for_creation(show_output=True)
    location = package.location

    acr = package.get_container_registry()

    package.pull()

    subprocess.check_call(['docker', 'login', acr.address, '-u', acr.username, '-p', acr.password])
    print('past login')

    subprocess.check_call(['docker', 'pull', location])
    print('past pull')

    print(location)
    print(os.getenv('CONTAINER_REGISTRY_ADDRESS') +'/' + str(model_name) + ':' + str(model_version))
    subprocess.check_call(['docker', 'tag', location, os.getenv('CONTAINER_REGISTRY_ADDRESS') +'/' + str(model_name) + ':' + str(model_version)])
    print('past tag')

    subprocess.check_call(['docker', 'login', os.getenv('CONTAINER_REGISTRY_ADDRESS'), '-u', os.getenv('CONTAINER_REGISTRY_USERNAME'), '-p', os.getenv('CONTAINER_REGISTRY_PASSWORD')])
    print('past login')

    subprocess.check_call(['docker', 'push', os.getenv('CONTAINER_REGISTRY_ADDRESS') +'/' + str(model_name) + ':' + str(model_version)])
    print('past push')


if __name__ == "__main__":
    main()