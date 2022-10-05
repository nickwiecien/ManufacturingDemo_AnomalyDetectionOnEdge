# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device import IoTHubModuleClient
from azure.iot.device import Message

import pandas as pd
from datetime import datetime
from azure.storage.queue import QueueClient
import os
import time
import json


# Event indicating client stop
stop_event = threading.Event()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()
    client.connect()

    # # Define function for handling received messages
    # async def receive_message_handler(message):
    #     # NOTE: This function only handles messages sent to "input1".
    #     # Messages sent to other inputs, or to the default, will be discarded
    #     if message.input_name == "input1":
    #         print("the data in the message received on input1 was ")
    #         print(message.data)
    #         print("custom properties are")
    #         print(message.custom_properties)
    #         print("forwarding mesage to output1")
    #         await client.send_message_to_output(message, "output1")

    # try:
    #     # Set handler on the client
    #     client.on_message_received = receive_message_handler
    # except:
    #     # Cleanup if failure occurs
    #     client.shutdown()
    #     raise

    return client


async def run_simulator(client):

    #Load master dataframe
    master_df = pd.read_parquet('./data/sensor.parquet', engine='pyarrow')
    master_df.drop(columns=['sensor_15', 'sensor_50', 'sensor_51', 'Unnamed: 0'], inplace=True)
    master_df = master_df.dropna()
    for x in master_df.columns:
        if 'sensor' in x:
            master_df[x] = master_df[x].astype(float)

    # Create connection to storage queue
    queue_client = QueueClient(os.getenv('STORAGE_ACCOUNT_URL'), os.getenv('STORAGE_ACCOUNT_QUEUE_NAME'), os.getenv('STORAGE_ACCOUNT_KEY'))

    while True:
        if len(queue_client.peek_messages())>0:
            message = queue_client.peek_messages()[0]
            m_content = int(message['content'])
            print(m_content)
            queue_client.clear_messages()
            new_index = m_content+1
            if new_index >= len(master_df):
                new_index=0
            
        else:
            new_index = 0
            if new_index >= len(master_df):
                new_index=0
            queue_client.send_message(str(new_index))
        
        queue_client.send_message(str(new_index))
        row = dict(master_df.iloc[new_index])
        row['timestamp'] = str(datetime.now())
        print(row)
        objstr = json.dumps(row)
        message =  Message(bytearray(objstr, 'utf-8'))
        # msg = Message(json.dumps(row))
        # msg.content_encoding = "utf-8"
        # msg.content_type = "application/json"
        client.send_message_to_output(message, 'output1')
        # client.send_message_to_output(msg, 'output2')
        await asyncio.sleep(60)


def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the simulator
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_simulator(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    asyncio.run(main())
