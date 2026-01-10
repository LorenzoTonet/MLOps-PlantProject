import pandas as pd
import numpy as np
import time
import json
from flask import Flask, Response
from dataset import synthetic_dataset

"""
This file sets up a Flask server that streams simulated sensor data statistics. 
The data is generated using the synthetic_dataset function from dataset.py.

Functions:
- stream_data: A generator that yields one row of the DataFrame as a JSON string at a time.
- stream_stats: A Flask route that serves the streamed data to clients.
"""

HOST = '127.0.0.1'  # localhost
PORT = 8001
STEP_TIME_SECONDS = 2  # waiting time between data points (seconds)

app = Flask(__name__)


def stream_data(df: pd.DataFrame):
    """
    A generator function that yields one row of the DataFrame at a time.

    Inputs:
    - df: The DataFrame containing the data to stream.
    """
    
    # convert multi-index columns to single level by joining with '_'
    flat_columns = [
        '_'.join(col).strip() for col in df.columns.values
    ]
    
    # convert dataframe to a list of dicts, one dict per row/index
    for index, row_tuple in enumerate(df.itertuples(index=True, name='PandasRow')):
        
        # create a dictionary for the row
        data_row = {
            "index": row_tuple[0], 
            "data": dict(zip(flat_columns, row_tuple[1:]))
        }
        
        # convert to json string
        json_data = json.dumps(data_row)
        
        # stream the JSON string followed by a newline
        yield f"{json_data}\n"
        
        # wait before sending the next data point
        time.sleep(STEP_TIME_SECONDS)
        
    # send a completion message
    yield json.dumps({"status": "Stream complete"}) + "\n"


@app.route('/stream_stats')
def stream_stats():
    """
    This function handles client requests to the /stream_stats endpoint. It streams simulated sensor data statistics
    as a series of JSON objects, one every STEP_TIME_SECONDS seconds.

    Outputs:
    - a flask Response object that streams JSON data to the client.
    """
    print(f"--- Client connected to /stream_stats. Generating and streaming data every {STEP_TIME_SECONDS}s. ---")
    
    # generate dataset
    stats_df = synthetic_dataset(6)
    
    return Response(
        stream_data(stats_df), 
        mimetype='application/json'
    )


if __name__ == '__main__':
    print("--- Starting Flask Server ---")
    print(f"Access stream at: http://{HOST}:{PORT}/stream_stats")
    
    # run
    app.run(host=HOST, port=PORT, debug=False)