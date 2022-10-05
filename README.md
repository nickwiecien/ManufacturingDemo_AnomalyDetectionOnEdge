# Manufacturing Demo - Anomaly Detection on Edge (MLOps with Azure ML)

This sample repository showcases a full end-to-end deployment of a ML solution for intelligent anomaly detection at the edge with integrated MLOps pipelines orchestrating all activities from code publication, model registration, all the way to edge deployment. 

Specifically, here we simulate manufacturing equipment which generates datapoints each minute and periodically enters into a 'BROKEN' state. We leverage a custom-built [autoencoder](https://www.tensorflow.org/tutorials/generative/autoencoder#third_example_anomaly_detection) running as an [IoT edge module](https://learn.microsoft.com/en-us/azure/iot-edge/about-iot-edge?view=iotedge-1.4) to identify when equipment is not performing as expected.

Multiple Azure services are used throughout this solution but it leverages [Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-machine-learning) and [Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/user-guide/what-is-azure-devops?view=azure-devops) heavily for model development and MLOps orchestration, respectively. See the 'Getting Started' section for more details on configuring your environment to load and run this demo solution.

![Anomaly Detection on Edge](img/end-to-end.png?raw=true "Anomaly Detection on Edge")

### Inside this Repo

This repository contains code samples for:

- Deploying a telemetry simulator to an IoT Device which streams data to an Azure IoT Hub 

- Consuming streaming telemetry data via Spark Streaming in Azure Databricks into an ADLS Gen2-backed Delta Table

- Training a customer autoencoder with TensorFlow/Keras using Azure ML (model tracking and registration performed via MLflow) both in a standalone Jupyter notebook and as part of an Azure Machine Learning Pipeline

- Automatic model retraining via scheduled runs of the Azure ML Pipeline

- Programmatic publication (continuous integration) of the AML pipeline into target workspaces mediated via Azure DevOps

- Programmatic deployment (continuous deployment) of models registered in an Azure ML workspace as a containerized edge module to an IoT device.

- Scoring of streaming telemetry data on device in real-time with the custom built autoencoder.

### Getting Started

<i>Details forthcoming on the following...</i>

- Standing Up Azure Resources

- Deploying an Azure VM as an IoT Device

- Seeding IoT Hub with Telemetry

- Configuring CI/CD Pipelines in Azure DevOps