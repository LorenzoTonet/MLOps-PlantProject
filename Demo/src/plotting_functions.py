import streamlit as st
import pandas as pd
import requests
import json
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
from datetime import datetime
import warnings

from src.config_handling import *
from src.plotting_functions import *
from src.data_generators import *
from src.plant_data_management import *

from src.stream_simulation import *

def plot_sensor(plant_name, sensor, SENSOR_COLORS, SENSOR_LABELS, Y_RANGES):
    """Helper function to create and return a single sensor plot"""
    df = st.session_state[f"data_{plant_name}"]
    
    if len(df) == 0:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 4))
    
    # Plot main line
    ax.plot(df["timestamp"], df[sensor], 
           linewidth=2.5, 
           color=SENSOR_COLORS[sensor],
           marker='o',
           markersize=4,
           label="Current value")
    
    # Plot standard deviation band
    ax.fill_between(df["timestamp"], 
                   df[sensor] - df[f"{sensor}_sd"], 
                   df[sensor] + df[f"{sensor}_sd"],
                   alpha=0.2,
                   color=SENSOR_COLORS[sensor],
                   label=f"±1 SD")
    
    # Add threshold lines if enabled
    if st.session_state.thresholds[sensor]["enabled"]:
        min_threshold = st.session_state.thresholds[sensor]["min"]
        max_threshold = st.session_state.thresholds[sensor]["max"]
        
        ax.axhline(y=min_threshold, 
                  color='red', 
                  linestyle='--', 
                  linewidth=2, 
                  alpha=0.7,
                  label=f'Min threshold ({min_threshold})')
        
        ax.axhline(y=max_threshold, 
                  color='red', 
                  linestyle='--', 
                  linewidth=2, 
                  alpha=0.7,
                  label=f'Max threshold ({max_threshold})')
        
        # Highlight critical zones
        ax.axhspan(Y_RANGES[sensor][0], min_threshold, 
                  alpha=0.1, color='red')
        ax.axhspan(max_threshold, Y_RANGES[sensor][1], 
                  alpha=0.1, color='red')
    
    # Current value and status
    current_value = df[sensor].iloc[-1]
    status = "OK"
    
    if st.session_state.thresholds[sensor]["enabled"]:
        if current_value < st.session_state.thresholds[sensor]["min"]:
            status = "TOO LOW"
        elif current_value > st.session_state.thresholds[sensor]["max"]:
            status = "TOO HIGH"
    
    ax.set_title(f"{SENSOR_LABELS[sensor]} - Current: {current_value:.1f} - {status}", 
                fontsize=13, 
                fontweight="bold")
    ax.set_ylim(Y_RANGES[sensor])
    ax.set_xlabel("Timestamp", fontsize=11)
    ax.set_ylabel(SENSOR_LABELS[sensor], fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    
    # Configure x-axis to prevent label overlap
    n_points = len(df)
    max_ticks = 10
    if n_points > max_ticks:
        tick_interval = max(1, n_points // max_ticks)
        tick_indices = list(range(0, n_points, tick_interval))
        ax.set_xticks([df["timestamp"].iloc[i] for i in tick_indices])
    
    # Rotate labels to prevent overlap
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig