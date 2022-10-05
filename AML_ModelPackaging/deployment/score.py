from azureml.core import Workspace, Model
import mlflow
import pandas as pd
import tensorflow as tf
import joblib
import mlflow.keras
import numpy as np
import json

model = None
scaler = None
threshold = None

def init():
    global model, scaler, threshold
    scaler = joblib.load('./deployment/scaler.pkl')
    model = mlflow.keras.load_model('./deployment/model')
    threshold = float(open('./deployment/threshold.txt', 'r').read())

def run(data):
    row_data = json.loads(data)
    df = pd.DataFrame(row_data)
    scaled_data = scaler.transform(df)
    reconstructions = model.predict(scaled_data)
    loss = tf.keras.losses.mae(reconstructions, scaled_data)
    loss.numpy()
    results = [x>threshold for x in loss.numpy()]
    return np.array([x>threshold for x in loss.numpy()], dtype=bool).tolist()