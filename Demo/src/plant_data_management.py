import json
from pathlib import Path
import streamlit as st
import random
import time
import pandas as pd

from datetime import datetime
from src.config_handling import *

def init_plant_data(plant_name):
    """
    Initialize data structures for a plant if not exists.
    Args:
        plant_name (str): Name of the plant.
    """
    if f"data_{plant_name}" not in st.session_state:
        st.session_state[f"data_{plant_name}"] = pd.DataFrame(columns=["timestamp"] + st.session_state.sensors + st.session_state.stdev_sensors)


def add_plant(plant_name, CONFIG_FILE):
    """Add a new plant to the monitoring list."""
    plant_name = plant_name.strip()
    if plant_name and plant_name not in st.session_state.plants:
        st.session_state.plants.append(plant_name)
        init_plant_data(plant_name)
        save_config(CONFIG_FILE)

def remove_plant(plant_name, CONFIG_FILE):
    """Remove a plant from the monitoring list."""
    if plant_name in st.session_state.plants:
        st.session_state.plants.remove(plant_name)

        data_key = f"data_{plant_name}"
        if data_key in st.session_state:
            del st.session_state[data_key]

        save_config(CONFIG_FILE)
