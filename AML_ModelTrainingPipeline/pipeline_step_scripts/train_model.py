from azureml.core import Run, Workspace, Datastore, Dataset
from azureml.data.datapath import DataPath
import os
import argparse
import shutil

import pandas as pd
import mlflow
from mlflow import pyfunc

from azureml.core import Workspace, Model
import numpy as np
import tensorflow as tf

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, losses
from tensorflow.keras.models import Model

# Parse input arguments
parser = argparse.ArgumentParser("Train autoencoder")
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--scaler_outputs', type=str, required=True)

# parser.add_argument('--model_description', type=str, required=True)

args, _ = parser.parse_known_args()
model_name = args.model_name
scaler_outputs = args.scaler_outputs
# model_description = args.model_description

# Get current run
current_run = Run.get_context()

#G et associated AML workspace
ws = current_run.experiment.workspace

# Read input dataset to pandas dataframe
train_dataset = current_run.input_datasets['Training_Data']
train_data = train_dataset.to_pandas_dataframe().astype(float)
test_dataset = current_run.input_datasets['Testing_Data']
test_data = test_dataset.to_pandas_dataframe().astype(float)
validation_dataset =  current_run.input_datasets['Validation_Data']
validation_data = validation_dataset.to_pandas_dataframe().astype(float)

################################# MODIFY #################################

# The intent of this block is to scale data appropriately and train
# a predictive model. Any normalizaton and training approach can be used.
# Serialized scalers/models can be passed forward to subsequent pipeline
# steps as PipelineData using the syntax below. Additionally, for 
# record-keeping, it is recommended to log performance metrics 
# into the current run.

class AnomalyDetector(Model):
  def __init__(self):
    super(AnomalyDetector, self).__init__()
    self.encoder = tf.keras.Sequential([
      layers.Dense(32, activation="relu"),
      layers.Dense(16, activation="relu"),
      layers.Dense(8, activation="relu")])

    self.decoder = tf.keras.Sequential([
      layers.Dense(16, activation="relu"),
      layers.Dense(32, activation="relu"),
      layers.Dense(49, activation="sigmoid")])

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded

autoencoder = AnomalyDetector()
autoencoder.compile(optimizer='adam', loss='mae')

import mlflow.tensorflow
mlflow.tensorflow.autolog(every_n_iter=1)

# Start the run
with mlflow.start_run(run_name='autoencoder-run') as run:
    run_id = run.info.run_id
    history = autoencoder.fit(train_data, train_data, 
          epochs=15, 
          batch_size=512,
          validation_data=(test_data, test_data),
          shuffle=True)
    mlflow.log_artifact(os.path.join(scaler_outputs, 'scaler.pkl'))
    model_uri = mlflow.get_artifact_uri("model")
    
    reconstructions = autoencoder.predict(train_data)
    train_loss = tf.keras.losses.mae(reconstructions, train_data)
    sd = np.std(train_loss[None,:])
    threshold = np.median(train_loss[None,:]) + (3*sd)
    with open('./threshold.txt', 'w') as file:
        file.write(str(threshold))
    mlflow.log_artifact('threshold.txt')
    
    # Champion vs. Challenger Logic
    # Prior to registering the model - optionally pull the current best
    # performing autoencoder from your model registry. Load this model
    # and calculate reconstruction losses for the holdout dataset. 
    # If reconstruction losses are larger (i.e., the model does a better 
    # job distinguishing bad from good then register the new model.
    # Otherwise do not proceeed with registration.
    
    mlflow.register_model(model_uri, model_name)


##########################################################################