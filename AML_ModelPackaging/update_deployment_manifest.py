import os
import argparse

def main():
    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--deployment_manifest_path",
        type=str,
        default="../IoT_MfgSiteEdgeDevice/config/deployment.amd64.json",
        help="Env file location"
    )
    parser.add_argument(
        "--deployment_template_path",
        type=str,
        default="../IoT_MfgSiteEdgeDevice/deployment.template.json",
        help="Deployment manifest template location"
    )
    args = parser.parse_args()
    lines = None
    with open(args.deployment_template_path, 'r') as file:
        lines = file.read()

    lines = lines.replace("${CONTAINER_REGISTRY_USERNAME}", os.getenv('CONTAINER_REGISTRY_USERNAME'))
    lines = lines.replace("${MODEL_VERSION_TAG}", os.getenv('MODEL_VERSION_TAG'))
    lines = lines.replace("${MODEL_NAME}", os.getenv('MODEL_NAME'))
    lines = lines.replace("${CONTAINER_REGISTRY_ADDRESS}", os.getenv('CONTAINER_REGISTRY_ADDRESS'))
    lines = lines.replace("${CONTAINER_REGISTRY_PASSWORD}", os.getenv('CONTAINER_REGISTRY_PASSWORD'))
    lines = lines.replace("${IOTHUB_CONNECTION_STRING}", os.getenv('IOTHUB_CONNECTION_STRING'))
    lines = lines.replace("${STORAGE_ACCOUNT_KEY}", os.getenv('STORAGE_ACCOUNT_KEY'))
    lines = lines.replace("${STORAGE_ACCOUNT_QUEUE_NAME}", os.getenv('STORAGE_ACCOUNT_QUEUE_NAME'))
    lines = lines.replace("${STORAGE_ACCOUNT_URL}", os.getenv('STORAGE_ACCOUNT_URL'))
    lines = lines.replace("${DEVICE_CONNECTION_STRING}", os.getenv('DEVICE_CONNECTION_STRING'))

    print(lines)

    os.makedirs('../IoT_MfgSiteEdgeDevice/config', exist_ok=True)

    with  open(args.deployment_manifest_path, 'w') as file:
        file.write(lines)


if __name__ == "__main__":
    main()