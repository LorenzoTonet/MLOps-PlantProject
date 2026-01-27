import pandas as pd
from Data.dataset import synthetic_dataset
import numpy as np
from neuralforecast import NeuralForecast
from neuralforecast.models import NHITS

"""
This script contains the functions to train an N-HITS model to forecast soil humidity levels for a plant, 
helping to determine when the next watering is needed. It uses cyclical time features and a 
watering intervention flag to improve prediction accuracy.

Functions:
- prepare_data(stats_df): prepares the dataset by adding necessary features for N-HITS.
- train(df): trains the N-HITS model on the provided DataFrame.
- predict(current_df, nf): predicts future soil humidity levels using the trained N-HITS model.
"""

def prepare_data(stats_df):
    """
    Prepare the dataset for training the N-HITS model. We will add the is_watering flag
    and cyclical time features (sine/cosine transforms of the hour of day). We'll also make every data
    feature between 0 and 1 for better model performance. 

    Inputs:
    - stats_df: DataFrame containing the time series data with humidity, temperature, and light levels.

    Outputs:
    - df: DataFrame formatted for NeuralForecast with necessary features.
    """
    df = stats_df.copy()

    df.columns = [col.strip() for col in df.columns]

    # N-HITS requires these 3 specific columns: 'ds', 'unique_id', 'y'
    # ds is the datetime in datetime format
    df['ds'] = df['timestamp'].astype('datetime64[ns]')
    # unique_id
    df['unique_id'] = df['plant_id']
    # y is the target variable, in our case soil humidity
    df['y'] = df['water_w_mean']

    # create two cyclical time features: time_sin and time_cos
    df['time_sin'] = np.sin((pd.to_datetime(df['ds']).dt.hour * 60 + pd.to_datetime(df['ds']).dt.minute) / 1440 * 2 * np.pi)
    df['time_cos'] = np.cos((pd.to_datetime(df['ds']).dt.hour * 60 + pd.to_datetime(df['ds']).dt.minute) / 1440 * 2 * np.pi)

    # we mark the watering and the next 3 samples with a new column 'is_watering'
    spike_indices = df.index[df['water_w_mean'].diff() > 2.0]
    df['is_watering'] = 0
    for idx in spike_indices:
        # mark the spike and the next 3 samples as watering event
        loc = df.index.get_loc(idx)
        df.iloc[loc : loc + 4, df.columns.get_loc('is_watering')] = 1

    return df


def train(df):
    '''
    Train the N-HITS model on the provided DataFrame.

    Inputs:
    - df: DataFrame containing the time series data with necessary features.
    
    Outputs:
    - model: Trained N-HITS model.
    '''

    # define all exogenous columns
    # cols I'll know in the future
    futr_exog = [col for col in df.columns if col in ['time_sin', 'time_cos', 'is_watering']]
    # cols I won't know in the future
    hist_exog = [col for col in df.columns if col not in ['ds', 'unique_id', 'y'] + futr_exog]

    # create NeuralForecast object

    horizon = 144  # how many steps to forecast (1 hour = 12 steps)
    input_size = 288 # how many past steps to use

    model = NHITS(
        h=horizon,
        input_size=input_size,
        futr_exog_list=futr_exog, 
        hist_exog_list=hist_exog,
        max_steps=1500,
        learning_rate=1e-3,
        scaler_type='standard' 
    )

    nf = NeuralForecast(models=[model], freq='5min')
    
    # train
    nf.fit(df=df[['unique_id', 'ds', 'y'] + futr_exog + hist_exog])

    # save the model
    nf.save(path = 'Models/NHITS_models/', overwrite=True)

    return nf


def predict(current_df, nf, threshold=30.0):
    '''
    Predict future values using the trained N-HITS model.

    Inputs:
    - current_df: DataFrame of the last steps (same len as the training input_size)
    
    Outputs:
    - forecast_df: DataFrame with predictions.
    '''

    horizon = 144

    # verify that we have enough past points
    if len(current_df) < 288:
        raise ValueError(f"NHITS needs 288 past points. You only provided {len(current_df)}.")

    # build the future dataframe with cyclical features
    future_dates = pd.date_range(
        start=pd.Timestamp(current_df['ds'].iloc[-1]) + pd.Timedelta(minutes=5), 
        periods=horizon, 
        freq='5min'
    )
    
    futr_df = pd.DataFrame({
        'unique_id': [current_df['unique_id'].iloc[0]] * horizon,
        'ds': future_dates
    })
    futr_df['ds'] = futr_df['ds'].astype('datetime64[ns]')
    
    futr_df['time_sin'] = np.sin(2 * np.pi * ((futr_df['ds'].dt.hour * 60) + futr_df['ds'].dt.minute) / 1440)
    futr_df['time_cos'] = np.cos(2 * np.pi * ((futr_df['ds'].dt.hour * 60) + futr_df['ds'].dt.minute) / 1440)
    futr_df['is_watering'] = 0  # assume no watering in the future

    # predict time series
    forecast_df = nf.predict(df=current_df, futr_df=futr_df)

    # compute the timestep of the next watering event (when the prediction goes below a threshold)
    # if there is no such event, we return the prediction at the last horizon step
    below_threshold = forecast_df[forecast_df['NHITS'] < threshold]
    if not below_threshold.empty:
        next_watering_time = below_threshold['ds'].iloc[0]
        print(f"Next watering event predicted at: {next_watering_time}")
        return 1, next_watering_time, forecast_df

    print("No watering event predicted within the forecast horizon.")

    return -1, forecast_df['NHITS'].iloc[-1], forecast_df
