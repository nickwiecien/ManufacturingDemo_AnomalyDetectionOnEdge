# Sample script for creating a scheduled run of an Azure Machine Learning Pipeline (Published PipelineEndpoint)

# Import required packages
from azureml.core import Workspace
from azureml.pipeline.core import PipelineEndpoint
from azureml.pipeline.core import Schedule, ScheduleRecurrence
import logging
import os
import argparse

parser = argparse.ArgumentParser("register")
parser.add_argument(
    "--mfg_site_id",
    type=str,
    default="mfg001",
    help="Manufacturing Site ID"
)
parser.add_argument(
    "--model_name",
    type=str,
    default="mfg-001_anomaly-detector",
    help="Model Name in AML Registry"
)
parser.add_argument(
    "--frequency",
    type=str,
    default="Week",
    help="Frequency of Schedule Execution"
)
parser.add_argument(
    "--interval",
    type=int,
    default=1,
    help="Interval of Schedule Execution"
)
args = parser.parse_args()
mfg_site_id = args.mfg_site_id
model_name = args.model_name
frequency = args.frequency
interval = args.interval
pipeline_endpoint_name = 'Autoencoder (Anomaly Detection) Model Training Pipeline'

# Connect to AML Workspace
ws=None
try:
    ws = Workspace.from_config()
except Exception:
    ws = Workspace(subscription_id=os.getenv('SUBSCRIPTION_ID'),  resource_group = os.getenv('RESOURCE_GROUP'), workspace_name = os.getenv('WORKSPACE_NAME'))
    
ds = ws.get_default_datastore()

pipeline_endpoint = PipelineEndpoint.get(ws, name=pipeline_endpoint_name)

name = f'{mfg_site_id}_{model_name}_schedule'.strip()
recurrence = ScheduleRecurrence(frequency=frequency, interval=interval)
schedules = Schedule.get_all(ws)
schedules = [x for x in schedules if x.name==name]

if len(schedules)==0:
    name = f'{mfg_site_id}_{model_name}_schedule'.strip()
    print(name)
    schedule = Schedule.create_for_pipeline_endpoint(ws, name, pipeline_endpoint.id, experiment_name=f'{name}_TRAINING_RUN', recurrence=recurrence, 
                                                      pipeline_parameters={'model_name': model_name, 'mfg_site_id': mfg_site_id})
else:
    if len(schedules)>1:
        for i in range(len(schedules)):
            schedules[i].disable()
    schedule = schedules[0]
    schedule.update(recurrence=recurrence, pipeline_parameters={'model_name': model_name, 'mfg_site_id': mfg_site_id}, status='Active') 
    
print([x for x in Schedule.get_all(ws) if x.name==name])