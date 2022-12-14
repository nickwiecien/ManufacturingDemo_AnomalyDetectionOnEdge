FROM mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.0.3-cudnn8-ubuntu18.04:20220902.v1

ENV AZUREML_CONDA_ENVIRONMENT_PATH /azureml-envs/tensorflow-2.4
# Create conda environment
RUN conda create -p $AZUREML_CONDA_ENVIRONMENT_PATH \
    python=3.7 pip=20.2.4

# Prepend path to AzureML conda environment
ENV PATH $AZUREML_CONDA_ENVIRONMENT_PATH/bin:$PATH

# Install pip dependencies
RUN HOROVOD_WITH_TENSORFLOW=1 \
    pip install 'matplotlib>=3.3,<3.4' \
                'psutil>=5.8,<5.9' \
                'tqdm>=4.59,<4.60' \
                'pandas==1.3.5' \
                'scipy>=1.5,<1.6' \
                'numpy>=1.10,<1.20' \
                'ipykernel~=6.0' \
                # upper bound azure-core to address typing-extensions conflict
                'azure-core<1.23.0' \
                'azureml-core~=1.43.0' \
                'azureml-defaults~=1.43.0' \
                'azureml-mlflow~=1.43.0' \
                'azureml-telemetry~=1.43.0' \
                'tensorboard==2.4.0' \
                'tensorflow-gpu==2.4.1' \
                'tensorflow-datasets==4.3.0' \
                'onnxruntime-gpu>=1.7,<1.8' \
                'protobuf~=3.20' \
                'horovod[tensorflow-gpu]==0.21.3' \
                'databricks-sql-connector==2.0.5' \
                'scikit-learn==0.22.1'

# This is needed for mpi to locate libpython
ENV LD_LIBRARY_PATH $AZUREML_CONDA_ENVIRONMENT_PATH/lib:$LD_LIBRARY_PATH
