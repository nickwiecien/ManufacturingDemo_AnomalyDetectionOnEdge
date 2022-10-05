# Step 2. Split Data
# Sample Python script designed to retrieve a pandas dataframe
# containing raw data, then split that into train and test subsets.

from azureml.core import Run, Workspace, Datastore, Dataset
from azureml.data.datapath import DataPath
import os
import argparse

import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import joblib
from numpy.random import seed

# Parse input arguments
parser = argparse.ArgumentParser("Split raw data into train/test subsets.")
parser.add_argument('--training_data', dest='training_data', required=True)
parser.add_argument('--testing_data', dest='testing_data', required=True)
parser.add_argument('--validation_data', dest='validation_data', required=True)
parser.add_argument('--splitscale_outputs', dest='splitscale_outputs', required=True)
parser.add_argument('--testing_size', type=float, required=True)

args, _ = parser.parse_known_args()
training_data = args.training_data
testing_data = args.testing_data
testing_size = args.testing_size
validation_data = args.validation_data
splitscale_outputs = args.splitscale_outputs

os.makedirs(splitscale_outputs, exist_ok=True)

# Get current run
current_run = Run.get_context()

# Get associated AML workspace
ws = current_run.experiment.workspace

# Read input dataset to pandas dataframe
raw_datset = current_run.input_datasets['Raw_Data']
df = raw_datset.to_pandas_dataframe()

################################# MODIFY #################################

# Optionally include data transformation steps here. These may also be
# included in a separate step entirely.

df = df.dropna()
df['timestamp'] = pd.to_datetime(df['timestamp'])

train_df = df[df['machine_status']=='NORMAL']
validate_df = df[df['machine_status']!='NORMAL']

full_df_train = train_df.drop(columns=['timestamp', 'machine_status'])
validate_df = validate_df.drop(columns=['timestamp', 'machine_status'])

scaler = MinMaxScaler()
scaler.fit(full_df_train)

full_df_train = scaler.transform(full_df_train)
full_df_bad  = scaler.transform(validate_df)

train_df, test_df = train_test_split(
    full_df_train, test_size=testing_size, random_state=21
)

import joblib
joblib.dump(scaler, os.path.join(splitscale_outputs, 'scaler.pkl'))

column_list = df.drop(columns=['timestamp', 'machine_status']).columns

##########################################################################

# Save train data to both train and test dataset locations.
os.makedirs(training_data, exist_ok=True)
os.makedirs(testing_data, exist_ok=True)
os.makedirs(validation_data, exist_ok=True)
pd.DataFrame(train_df, columns=column_list).to_csv(os.path.join(training_data, 'training_data.csv'), index=False)
pd.DataFrame(test_df, columns=column_list).to_csv(os.path.join(testing_data, 'testing_data.csv'), index=False)
pd.DataFrame(validate_df, columns=column_list).to_csv(os.path.join(validation_data, 'testing_data.csv'), index=False)
