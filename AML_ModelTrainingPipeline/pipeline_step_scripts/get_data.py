# Step 1. Get Data
# Sample Python script designed to load data from a target data source,
# and export as a tabular dataset

from azureml.core import Run, Workspace, Datastore, Dataset
from databricks import sql as dbsql 
import pandas as pd 
import os
import argparse
import numpy as np

# Parse input arguments
parser = argparse.ArgumentParser("Get raw data from a selected datastore and register in AML workspace")
parser.add_argument('--raw_dataset', dest='raw_dataset', required=True)
parser.add_argument('--mfg_site_id', type=str, required=True)

args, _ = parser.parse_known_args()
raw_dataset = args.raw_dataset
mfg_site_id = args.mfg_site_id

# Get current run
current_run = Run.get_context()

# Get associated AML workspace
ws = current_run.experiment.workspace

# Connect to default blob datastore
ds = ws.get_default_datastore()

kv = ws.get_default_keyvault()

databricks_pat = kv.get_secret('dbxpat')
http_path = kv.get_secret('dbxhttppath')
server_hostname = kv.get_secret('dbxservername')

################################# MODIFY #################################

# The intent of this block is to load from a target data source. This
# can be from an AML-linked datastore or a separate data source accessed
# using a different SDK. Any initial formatting operations can be be 
# performed here as well.

# Read all raw data from blob storage & convert to a pandas data frame
connection = dbsql.connect( 
    server_hostname = server_hostname,
    http_path = http_path,
    access_token = databricks_pat
)
 
# Represent the query as a string 
sql_query = f"SELECT * FROM default.{mfg_site_id}" 
 
# Execute the query 
with connection.cursor() as cursor: 
# Get the data 
    cursor.execute(sql_query) 
    data = cursor.fetchall() 
    cursor.execute(f"SHOW COLUMNS IN default.{mfg_site_id}") 
    columns = cursor.fetchall() 

columns = [column[0] for column in columns] 
raw_df = pd.DataFrame(data=data, columns=columns)

##########################################################################

# Make directory on mounted storage for output dataset
os.makedirs(raw_dataset, exist_ok=True)

# Save modified dataframe
raw_df.to_csv(os.path.join(raw_dataset, 'raw_data.csv'), index=False)