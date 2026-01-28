import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from Demo.src.config_handling import *
from Demo.src.plotting_functions import *
from Demo.src.data_generators import *
from Demo.src.plant_data_management import *

from Demo.src.stream_simulation import *

def plot_sensor(plant_name, sensor, SENSOR_COLORS, SENSOR_LABELS, Y_RANGES, MAX_POINTS):
    """Helper function to create and return a single sensor plot"""
    fake_df = st.session_state[f"data_{plant_name}"].copy()
    df = fake_df.iloc[-MAX_POINTS:]
    
    if len(df) == 0:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 4))
    
    # Plot main line
    ax.plot(df["timestamp"], df[f"{sensor}_w_mean"], 
           linewidth=2.5, 
           color=SENSOR_COLORS[sensor],
           marker='o',
           markersize=4,
           label="Current value")
    
    # Plot standard deviation band
    ax.fill_between(df["timestamp"], 
                   df[f"{sensor}_w_mean"] - df[f"{sensor}_w_sd"], 
                   df[f"{sensor}_w_mean"] + df[f"{sensor}_w_sd"],
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
        
        #critical zones
        ax.axhspan(Y_RANGES[sensor][0], min_threshold, 
                  alpha=0.1, color='red')
        ax.axhspan(max_threshold, Y_RANGES[sensor][1], 
                  alpha=0.1, color='red')
    
    current_value = df[f"{sensor}_w_mean"].iloc[-1]
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
    
    n_points = len(df)
    max_ticks = 10
    if n_points > max_ticks:
        tick_interval = max(1, n_points // max_ticks)
        tick_indices = list(range(0, n_points, tick_interval))
        ax.set_xticks([df["timestamp"].iloc[i] for i in tick_indices])
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

def plot_sensor_wtr(
    plant_name,
    sensor,
    preddf,
    SENSOR_COLORS,
    SENSOR_LABELS,
    Y_RANGES,
    MAX_POINTS
):
    """Helper function to create and return a single sensor plot with prediction"""

    # ---- Historical data ----
    fake_df = st.session_state[f"data_{plant_name}"].copy()
    fake_df["timestamp"] = pd.to_datetime(fake_df["timestamp"])
    df = fake_df.iloc[-MAX_POINTS:]

    if len(df) == 0:
        return None

    # ---- Prediction data ----
    preddf = preddf.copy()
    preddf["ds"] = pd.to_datetime(preddf["ds"])

    # ---- Build combined axis ----
    xx_hist = df["timestamp"].tolist()
    yy_hist = df[f"{sensor}_w_mean"].tolist()

    xx_pred = preddf["ds"].tolist()
    yy_pred = preddf["NHITS"].tolist()

    xx_all = xx_hist + xx_pred

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(14, 4))

    # Historical line
    ax.plot(
        xx_hist,
        yy_hist,
        linewidth=2.5,
        color=SENSOR_COLORS[sensor],
        marker="o",
        markersize=4,
        label="Current value"
    )

    # SD band (only historical)
    ax.fill_between(
        xx_hist,
        df[f"{sensor}_w_mean"] - df[f"{sensor}_w_sd"],
        df[f"{sensor}_w_mean"] + df[f"{sensor}_w_sd"],
        alpha=0.2,
        color=SENSOR_COLORS[sensor]
    )

    # Connection line
    if xx_pred:
        ax.plot(
            [xx_hist[-1], xx_pred[0]],
            [yy_hist[-1], yy_pred[0]],
            color="orange",
            linewidth=2.5,
            linestyle="--"
        )

    # Prediction line
    ax.plot(
        xx_pred,
        yy_pred,
        linewidth=2.5,
        color="orange",
        marker="o",
        markersize=4,
        label="Prediction"
    )

    # ---- Thresholds ----
    if st.session_state.thresholds[sensor]["enabled"]:
        min_th = st.session_state.thresholds[sensor]["min"]
        max_th = st.session_state.thresholds[sensor]["max"]

        ax.axhline(
            y=min_th,
            color="red",
            linestyle="--",
            linewidth=2,
            alpha=0.7,
            label=f"Min threshold ({min_th})"
        )

        ax.axhline(
            y=max_th,
            color="red",
            linestyle="--",
            linewidth=2,
            alpha=0.7,
            label=f"Max threshold ({max_th})"
        )

        ax.axhspan(Y_RANGES[sensor][0], min_th, alpha=0.1, color="red")
        ax.axhspan(max_th, Y_RANGES[sensor][1], alpha=0.1, color="red")

    # ---- Current status ----
    current_value = yy_hist[-1]
    status = "OK"

    if st.session_state.thresholds[sensor]["enabled"]:
        if current_value < st.session_state.thresholds[sensor]["min"]:
            status = "TOO LOW"
        elif current_value > st.session_state.thresholds[sensor]["max"]:
            status = "TOO HIGH"

    # ---- Labels & style ----
    ax.set_title(
        f"{SENSOR_LABELS[sensor]} - Current: {current_value:.1f} - {status}",
        fontsize=13,
        fontweight="bold"
    )
    ax.set_ylim(Y_RANGES[sensor])
    ax.set_xlabel("Timestamp", fontsize=11)
    ax.set_ylabel(SENSOR_LABELS[sensor], fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    
    n_points = len(xx_all)
    max_ticks = 10
    if n_points > max_ticks:
        tick_interval = max(1, n_points // max_ticks)
        ax.set_xticks(xx_all[::tick_interval])

    
    # ---- X axis formatting ----
    time_fmt = mdates.DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(time_fmt)

    
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    plt.tight_layout()
    return fig
