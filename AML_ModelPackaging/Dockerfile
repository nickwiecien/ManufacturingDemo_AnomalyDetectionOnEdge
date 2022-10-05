FROM mcr.microsoft.com/azureml/tensorflow-2.4-ubuntu18.04-py37-cpu-inference:20220516.v3

# Install pip dependencies
RUN pip install 'pandas==1.3.5' \
                'azure-core<1.23.0' \
                'azureml-core~=1.43.0' \
                'azureml-defaults~=1.43.0' \
                'azureml-mlflow~=1.43.0' \
                'tensorflow==2.4.1' \
                'tensorflow-datasets==4.3.0' \
                'scikit-learn==0.22.1'