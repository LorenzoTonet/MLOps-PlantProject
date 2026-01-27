"""
Streamlit dashboard for greenhouse monitoring
"""

import streamlit as st
import pandas as pd

import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings

from src.config_handling import *
from src.plotting_functions import *
from src.data_generators import *
from src.plant_data_management import *
from src.wab_stream import *
from src.stream_simulation import *

warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------

CONFIG_FILE = Path("greenhouse_info.json")
config = load_config(CONFIG_FILE)

Y_RANGES = {
    "light": (0, 1023),
    "temperature": (0, 50),
    "humidity": (0, 100),
    "water": (0, 1023),
}

SENSOR_LABELS = {
    "light": "Light (lux)",
    "temperature": "Temperature (°C)",
    "humidity": "Air Humidity (%)",
    "water": "Water level (%)"
}

SENSOR_COLORS = {
    "light": "#F5A623",
    "temperature": "#E74C3C",
    "humidity": "#8B4513",
    "water": "#4A90E2"
}


st.set_page_config(page_title="Greenhouse Monitor", layout="wide")
st.title("Greenhouse Monitoring Dashboard")


if "sensors" not in st.session_state:
    st.session_state.sensors = config["sensors"]

if "plants" not in st.session_state:
    st.session_state.plants = config["plants"]

if "stdev_sensors" not in st.session_state:
    st.session_state.stdev_sensors = config["stdev_sensors"]

if "sensor_gen" not in st.session_state:
    st.session_state.sensor_gen = sensor_data_generator("Data/plant_data.csv")

# Initialize flag for monitoring state
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# Initialize default thresholds for each sensor
if "thresholds" not in st.session_state:
    st.session_state.thresholds = {
        "light": {"min": 200, "max": 800, "enabled": False},
        "temperature": {"min": 15, "max": 30, "enabled": False},
        "humidity": {"min": 40, "max": 80, "enabled": False},
        "water": {"min": 300, "max": 900, "enabled": False},
    }

# -----------------------------
# SIDEBAR - CONNECTION SETTINGS
# -----------------------------
st.sidebar.header("Connection Settings")

connection_mode = st.sidebar.radio(
    "Data Source",
    ["WaB", "Random Data", "Simulated"],
    index=1
)

if connection_mode == "WaB":
    default_project = st.session_state.get("wab_project", "sensor-read-test")
    default_entity = st.session_state.get("wab_entity", "MLOps-PlantProject")
    wab_project = st.sidebar.text_input("W&B Project", default_project)
    wab_entity = st.sidebar.text_input("W&B Entity", default_entity)
    st.session_state.wab_project = wab_project
    st.session_state.wab_entity = wab_entity
    st.sidebar.markdown(f"**W&B Project:** `{wab_entity}/{wab_project}`")
    st.sidebar.markdown("---")
    st.sidebar.subheader("W&B Polling Settings")
    
    poll_interval = st.sidebar.slider(
        "Check for new data every (seconds)",
        min_value=5,
        max_value=60,
        value=10,
        step=5,
        help="How often to check W&B for new data"
    )
    
    st.session_state.wab_poll_interval = poll_interval
    
    # Show W&B connection status
    show_wab_status()


elif connection_mode == "Random Data":
    st.sidebar.markdown("**Mode:** Random Data Generation")
elif connection_mode == "Simulated":
    st.sidebar.markdown("**Mode:** Simulated Data")

st.sidebar.markdown("---")

# -----------------------------
# SIDEBAR - PLANT SELECTION
# -----------------------------
st.sidebar.header("Plant Selection")

selected_plant = st.sidebar.selectbox(
    "Select Plant to Monitor",
    st.session_state.plants,
    key="selected_plant",
    index=0
)


st.sidebar.markdown("---")

with st.sidebar.expander("Add New Plant"):
    with st.form("add_plant_form", clear_on_submit=True):
        new_plant_name = st.text_input("Plant name")
        submitted = st.form_submit_button("Add")

        if submitted and new_plant_name.strip():
            add_plant(new_plant_name, CONFIG_FILE)
            st.success(f"Plant '{new_plant_name}' added")
            st.rerun()

with st.sidebar.expander("Remove Plant"):
    if st.session_state.plants:
        plant_to_remove = st.selectbox(
            "Select plant to remove",
            st.session_state.plants,
            key="plant_to_remove",
        )

        confirm = st.button("Remove", type="primary")

        if confirm:
            remove_plant(plant_to_remove, CONFIG_FILE)
            st.success(f"Plant '{plant_to_remove}' removed")
            st.rerun()
    else:
        st.info("No plants to remove.")

st.sidebar.markdown("---")

# -----------------------------
# SIDEBAR - THRESHOLDS SETTINGS
# -----------------------------
st.sidebar.header("Critical Thresholds")

for sensor in st.session_state.sensors:
    with st.sidebar.expander(f"{SENSOR_LABELS[sensor]}"):
        enabled = st.checkbox(
            "Enable thresholds",
            value=st.session_state.thresholds[sensor]["enabled"],
            key=f"enable_{sensor}"
        )
        st.session_state.thresholds[sensor]["enabled"] = enabled
        
        if enabled:
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input(
                    "Min",
                    min_value=float(Y_RANGES[sensor][0]),
                    max_value=float(Y_RANGES[sensor][1]),
                    value=float(st.session_state.thresholds[sensor]["min"]),
                    key=f"min_{sensor}"
                )
                st.session_state.thresholds[sensor]["min"] = min_val
            
            with col2:
                max_val = st.number_input(
                    "Max",
                    min_value=float(Y_RANGES[sensor][0]),
                    max_value=float(Y_RANGES[sensor][1]),
                    value=float(st.session_state.thresholds[sensor]["max"]),
                    key=f"max_{sensor}"
                )
                st.session_state.thresholds[sensor]["max"] = max_val

st.sidebar.markdown("---")

# -----------------------------
# PARAMETERS
# -----------------------------
st.sidebar.header("Settings")
REFRESH_INTERVAL = st.sidebar.slider("Refresh interval (seconds)", 0.1, 5.0, 1.0)
MAX_POINTS = st.sidebar.slider("Number of samples to show", 50, 500, 150)

st.sidebar.markdown("---")

# -----------------------------
# MONITORING CONTROLS
# -----------------------------
st.sidebar.header("Monitoring Controls")

if st.sidebar.button("Start Monitoring" if not st.session_state.monitoring else "Pause Monitoring", 
                     type="primary", use_container_width=True):
    st.session_state.monitoring = not st.session_state.monitoring
    st.rerun()


if st.session_state.monitoring:
    st.sidebar.success("Status: Recording")
else:
    st.sidebar.info("Status: Paused")

SENSORS = st.session_state.sensors

# -----------------------------
# INITIALIZE SESSION STATE
# -----------------------------

# Initialize all plants
for plant in st.session_state.plants:
    init_plant_data(plant)

# -----------------------------
# DISPLAY CURRENT PLANT STATUS
# -----------------------------
st.subheader(f"Monitoring: {selected_plant}")

df = st.session_state[f"data_{selected_plant}"]
if len(df) == 0:
    st.info("Waiting for live data...")

chart_placeholders = {}
for sensor in SENSORS:
    st.markdown(f"### {SENSOR_LABELS[sensor]}")
    chart_placeholders[sensor] = st.empty()

# -----------------------------
# LIVE PLOTTING LOOP - SMOOTH UPDATE
# -----------------------------

if st.session_state.monitoring:
    
    while st.session_state.monitoring:

        if connection_mode == "Random Data":
            snapshot = generate_snapshot()
        elif connection_mode == "Simulated":
            snapshot = [next(st.session_state.sensor_gen)]
        elif connection_mode == "WaB":
            snapshot = fetch_wab_data()
            print(f"Fetched new samples from W&B")
            if len(snapshot) > 0:
                print(snapshot)
        else:
            snapshot = []

        for sample in snapshot:
            
            if "plant" not in sample:
                continue
            
            plant_name = sample["plant"]
            
            if plant_name not in st.session_state.plants:
                continue
            
            df = st.session_state[f"data_{plant_name}"]

            df.loc[len(df)] = sample

            # Keep only last MAX_POINTS samples
            if len(df) > MAX_POINTS:
                df = df.iloc[-MAX_POINTS:].reset_index(drop=True)

            st.session_state[f"data_{plant_name}"] = df

        for sensor in SENSORS:
            fig = plot_sensor(selected_plant, sensor, SENSOR_COLORS, SENSOR_LABELS, Y_RANGES)
            if fig:
                chart_placeholders[sensor].pyplot(fig)
                plt.close(fig)

        time.sleep(REFRESH_INTERVAL)
        
else:
    for sensor in SENSORS:
        fig = plot_sensor(selected_plant, sensor, SENSOR_COLORS, SENSOR_LABELS, Y_RANGES)
        if fig:
            chart_placeholders[sensor].pyplot(fig)
            plt.close(fig)