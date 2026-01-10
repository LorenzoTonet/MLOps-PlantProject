import numpy as np
import pandas as pd

"""
This file implements a function that generates a synthetic dataset simulating soil humidity over time based 
on environmental conditions such as light and temperature.
The functions incorporates soil and crop parameters to simulate realistic evapotranspiration dynamics.

Functions:
- get_light(t, L_peak): models light intensity as a truncated cosine wave with noise and cloud cover effects.
- get_temperature(t, T_avg, A, t_lag): models temperature as a lagged and dampened cosine wave with noise.
- calculate_lambda(T, L, theta, K_soil, K_crop, lambda_base, c_temp, c_light, theta_pwp): calculates the decay rate based on environmental and soil conditions.
- syntethic_dataset(...): generates a synthetic dataset of soil humidity over time given environmental conditions.
"""


def get_light(t, L_peak):
    """
    This function models light as a truncated cosine wave with peak at noon.

    Inputs:
    - t: time in hours
    - L_peak: peak light intensity

    Outputs:
    - L: light intensity at time t
    """

    t_peak = 720.0  # light peaks at noon

    # cosine function for smooth daily cycle
    cos_val = np.cos((2 * np.pi / 1440) * (t - t_peak))

    # truncate at 0 (night time) and scale by peak intensity
    L = np.maximum(0, L_peak * cos_val)

    # add high-frequency noise for realism
    noise = np.random.normal(0, 5)

    # model cloud cover dips (e.g., 5% chance of a cloud event)
    # TODO: make this more sophisticated later, e.g., duration, dependent on previous state, etc.
    if np.random.rand() < 0.05 and L > 0:
        cloud_factor = np.random.uniform(0.1, 0.4)
        L *= (1 - cloud_factor)

    return np.maximum(0, L + noise)


def get_temperature(t, T_avg, A, t_lag):
    """
    This function models temperature as a lagged and dampened cosine wave.

    Inputs:
    - t: time in minutes
    - T_avg: average daily temperature
    - A: amplitude of temperature swing
    - t_lag: time lag in minutes for temperature peak

    Outputs:
    - T: temperature at time t
    """

    t_peak = 720.0 + t_lag  # temperature peaks some t_lag after light peak

    # cosine function for daily cycle
    T = T_avg + A * np.cos((2 * np.pi / 1440) * (t - t_peak))
    
    # add measurement noise
    return T + np.random.normal(0, 0.2)


def calculate_lambda(T, L, theta, K_soil, K_crop, lambda_base, c_temp, c_light, theta_pwp):
    """
    This function calculates the decay rate (lambda) based on environmental and soil conditions.
    The function is K_soil * lambda_base + K_crop * (c_temp * T + c_light * L)

    Inputs:
    - T: temperature (°C)
    - L: light intensity (light units)
    - theta: current soil humidity (%)
    - K_soil: soil drainage factor
    - K_crop: crop coefficient
    - lambda_base: base decay rate (per minute)
    - c_temp: temperature sensitivity (per minute per degree °C)
    - c_light: light sensitivity (per minute per light unit)
    - theta_pwp: permanent wilting point (%)

    Outputs:
    - lambda_total: total decay rate (per minute)
    """

    # decay rate including soil property influence
    lambda_base_soil = lambda_base * K_soil

    # scale by crop coefficient
    lambda_env = K_crop * (c_temp * T + c_light * L)

    # total potential decay rate
    lambda_total = lambda_base_soil + lambda_env

    # water stress reduction (stress_coeff)
    # the decay rate drops dramatically as humidity approaches PWP
    # This prevents the plant from using water when it's under severe stress
    if theta <= theta_pwp:
        stress_coeff = (theta / theta_pwp) ** 2  # non linear drop-off
        stress_coeff = np.clip(stress_coeff, 0.05, 1.0)  # cap at a minimum
        lambda_total *= stress_coeff

    return lambda_total


def full_data(total_time_minutes, time_step, theta_init=90.0, theta_pwp=15.0, K_soil=0.8, K_crop=0.6, lambda_base=0.00005, 
                      c_temp=0.000015, c_light=0.000020, L_peak=1000, T_avg=22.0, T_amplitude=3.0, T_lag=120.0):
    """
    Generates a synthetic dataset of soil humidity over time given environmental conditions.
    The formula used is:
    theta(t) = (theta_i - theta_pwp) * exp(-lambda * t) + theta_pwp
    where lambda is dynamically calculated based on temperature, light, and soil/crop parameters.

    Inputs:
    - total_time_minutes: total simulation time in minutes
    - time_step: duration of one time step in minutes

    - theta_init: initial soil humidity (% at Field Capacity)
    - theta_pwp: permanent wilting point (%)
    - K_soil: soil drainage factor

    - K_crop: crop coefficient
    - lambda_base: base decay rate (per minute)

    - c_temp: temperature sensitivity (per minute per degree °C)
    - T_avg: average daily temperature (°C)
    - T_amplitude: amplitude of daily temperature swing (°C)
    - T_lag: thermal lag in hours

    - c_light: light sensitivity (per minute per light unit)
    - L_peak: peak light intensity (light units)
    
    Outputs:
    - time: array of time points
    - humidity_data: array of soil humidity values over time
    - light_data: array of light intensity values over time
    - temp_data: array of temperature values over time
    """

    # initial state
    total_steps = int(total_time_minutes / time_step)
    time = np.linspace(0, total_time_minutes, total_steps)  # time in minutes

    humidity_data = np.zeros(total_steps)
    humidity_data[0] = theta_init
    current_humidity = theta_init
    watering_threshold = 25.0

    
    light_data = np.zeros(total_steps)
    temp_data = np.zeros(total_steps)

    for i in range(total_steps - 1):
        t_minutes = time[i]

        # get inputs at current time
        L_i = get_light(t_minutes, L_peak)
        T_i = get_temperature(t_minutes, T_avg, T_amplitude, T_lag)
        light_data[i] = L_i
        temp_data[i] = T_i

        # if the humidity is below a threshold, simulate watering
        if current_humidity <= watering_threshold:
            current_humidity = theta_init

        # calculate lambda (decay rate)
        lambda_i = calculate_lambda(T_i, L_i, current_humidity, K_soil, K_crop, lambda_base, c_temp, c_light, theta_pwp)

        # update humidity
        current_humidity = (current_humidity - theta_pwp) * np.exp(-lambda_i * time_step) + theta_pwp

        # ensure non-negative humidity
        current_humidity = np.maximum(0, current_humidity)

        # save result
        humidity_data[i + 1] = current_humidity

    return time, humidity_data, light_data, temp_data

def synthetic_dataset(k, total_time_minutes=7200, time_step=10, theta_init=90.0, theta_pwp=15.0, K_soil=0.8, K_crop=0.6, lambda_base=0.00005, 
                      c_temp=0.000015, c_light=0.000020, L_peak=1000, T_avg=22.0, T_amplitude=3.0, T_lag=120.0):
    """
    This function computes some statistics on the full data obtained trough simulation of full_data and writes these statistics in a file.
    We are interested in mean, min, max, quartiles of humidity, light and temperature. We also return the statistics as a pandas DataFrame.

    Inputs:
    - inputs of full_data function
    - k: number of data points to consider for each statistic calculation

    Outputs:
    - pandas DataFrame with statistics
    """

    time, humidity_data, light_data, temp_data = full_data(total_time_minutes, time_step, theta_init, theta_pwp, K_soil, K_crop, lambda_base, 
                                                           c_temp, c_light, L_peak, T_avg, T_amplitude, T_lag)

    # let the length of data be multiple of k
    data_len = len(humidity_data)
    num_blocks = data_len // k
    humidity_blocks = humidity_data[:num_blocks * k]
    light_blocks = light_data[:num_blocks * k]
    temp_blocks = temp_data[:num_blocks * k]
    time_blocks = time[:num_blocks * k]
    
    # reshape the data in row major order to have each block of k elements in a row
    humidity_reshaped = humidity_blocks.reshape(num_blocks, k)
    light_reshaped = light_blocks.reshape(num_blocks, k)
    temp_reshaped = temp_blocks.reshape(num_blocks, k)
    
    #compute statistics
    stats = ['mean', 'min', 'max', '25%', '75%']
    
    # mean
    mean_hum = np.mean(humidity_reshaped, axis=1)
    mean_light = np.mean(light_reshaped, axis=1)
    mean_temp = np.mean(temp_reshaped, axis=1)
    
    # min/max
    min_hum = np.min(humidity_reshaped, axis=1)
    max_hum = np.max(humidity_reshaped, axis=1)
    min_light = np.min(light_reshaped, axis=1)
    max_light = np.max(light_reshaped, axis=1)
    min_temp = np.min(temp_reshaped, axis=1)
    max_temp = np.max(temp_reshaped, axis=1)
    
    # quartiles (25th and 75th percentiles)
    q25_hum = np.percentile(humidity_reshaped, 25, axis=1)
    q75_hum = np.percentile(humidity_reshaped, 75, axis=1)
    q25_light = np.percentile(light_reshaped, 25, axis=1)
    q75_light = np.percentile(light_reshaped, 75, axis=1)
    q25_temp = np.percentile(temp_reshaped, 25, axis=1)
    q75_temp = np.percentile(temp_reshaped, 75, axis=1)
    
    # create the dataframe
    column_index = pd.MultiIndex.from_product([
        ['humidity', 'light_data', 'temp_data'], 
        stats
    ], names=['Variable', 'Statistic'])
    
    data_combined = np.column_stack([
        mean_hum, min_hum, max_hum, q25_hum, q75_hum,
        mean_light, min_light, max_light, q25_light, q75_light,
        mean_temp, min_temp, max_temp, q25_temp, q75_temp
    ])

    stats_df = pd.DataFrame(
        data_combined,
        columns=column_index
    )

    # TODO: fix the filesystem path as needed
    with open('Data/synthetic_dataset_stats.csv', 'w') as f:
        stats_df.to_csv(f)
        print("Synthetic dataset statistics saved to Data/synthetic_dataset_stats.csv")

    return stats_df
