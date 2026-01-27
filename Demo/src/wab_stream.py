"""
W&B data fetching for greenhouse monitoring with smart polling
"""

import wandb
import streamlit as st
from datetime import datetime
import time
import os

from src.config_handling import load_api_key

def initialize_wandb_api():
    """
    Initialize W&B API with authentication.
    
    Returns:
        wandb.Api: Authenticated W&B API object, or None if authentication fails
    """
    try:
        
        api_key = load_api_key("api_key.json")
        
        if not api_key:
            st.sidebar.error("W&B API key not found in api_key.json")
            return None
        
        # Initialize and return API
        os.environ["WANDB_API_KEY"] = api_key
        api = wandb.Api()
        return api
        
    except Exception as e:
        st.sidebar.error(f"W&B authentication failed: {str(e)}")
        return None


def fetch_wab_data():
    """
    Fetches the latest sensor data from W&B with smart caching.
    Only fetches new data when available, avoiding unnecessary API calls.
    """
    try:
        # Initialize tracking variables
        if "last_wab_fetch_time" not in st.session_state:
            st.session_state.last_wab_fetch_time = 0
        
        if "last_wab_timestamp" not in st.session_state:
            st.session_state.last_wab_timestamp = None
        
        if "last_wab_step" not in st.session_state:
            st.session_state.last_wab_step = -1
        
        if "wab_api" not in st.session_state:
            st.session_state.wab_api = None
        
        # Minimum time between API calls (in seconds)
        MIN_FETCH_INTERVAL = st.session_state.get("wab_poll_interval", 10)
        
        current_time = time.time()
        time_since_last_fetch = current_time - st.session_state.last_wab_fetch_time
        
        if time_since_last_fetch < MIN_FETCH_INTERVAL:
            return []
        
        st.session_state.last_wab_fetch_time = current_time

        if st.session_state.wab_api is None:
            st.session_state.wab_api = initialize_wandb_api()
            
        if st.session_state.wab_api is None:
            return []
        
        api = st.session_state.wab_api
        
        # Get project from session state
        project = f"{st.session_state.wab_entity}/{st.session_state.wab_project}"
        
        # Get the most recent run
        runs = api.runs(project, order="-created_at")
        if not runs:
            st.sidebar.warning("No runs found in W&B project")
            return []
        
        latest_run = runs[0]
        current_step = latest_run.lastHistoryStep
        
        # CORREZIONE: controlla se c'è un nuovo step PRIMA di fetchare
        if current_step <= st.session_state.last_wab_step:
            return []
        
        # CORREZIONE: usa scan_history correttamente
        # Opzione 1: prendi solo l'ultimo step
        history = list(latest_run.scan_history(min_step=current_step))
        
        # Opzione 2: se la prima non funziona, prova questa
        # history = list(latest_run.scan_history())
        # if history:
        #     history = [history[-1]]  # prendi solo l'ultimo record
        
        if not history:
            return []
        
        last_record = history[-1]
        
        # CORREZIONE: il timestamp check è ridondante se già controlli lo step
        # ma lo lascio come ulteriore sicurezza
        record_timestamp = last_record.get("_timestamp") or last_record.get("timestamp")
        if record_timestamp and record_timestamp == st.session_state.last_wab_timestamp:
            return []
        
        wanted_keys = {
            "plant",
            "timestamp",
            "light_value", "light_w_sd",
            "temp_value", "temp_w_sd",
            "humid_value", "humid_w_sd",
            "water_value", "water_w_sd",
        }
        
        filtered_data = {
            k: last_record[k]
            for k in wanted_keys
            if k in last_record
        }
        
        sensor_data = {
            "plant": filtered_data.get("plant", "plant_1"),
            "timestamp": format_timestamp(filtered_data.get("timestamp")),
            
            "light": filtered_data.get("light_value", 0.0),
            "light_sd": filtered_data.get("light_w_sd", 0.0),
            
            "temperature": filtered_data.get("temp_value", 0.0),
            "temperature_sd": filtered_data.get("temp_w_sd", 0.0),
            
            "humidity": filtered_data.get("humid_value", 0.0),
            "humidity_sd": filtered_data.get("humid_w_sd", 0.0),
            
            "water": filtered_data.get("water_value", 0.0),
            "water_sd": filtered_data.get("water_w_sd", 0.0),
        }
        
        # Aggiorna DOPO aver creato sensor_data con successo
        st.session_state.last_wab_step = current_step
        st.session_state.last_wab_timestamp = record_timestamp
        
        return [sensor_data]
        
    except Exception as e:
        st.sidebar.error(f"W&B Error: {str(e)}")
        import traceback
        st.sidebar.error(traceback.format_exc())  # AGGIUNTO: per debug più dettagliato
        return []
    
def format_timestamp(ts):
    """
    Formats timestamp to HH:MM:SS format.
    Args:
        ts (int, float, str): Timestamp in seconds or nanoseconds, or string.
    Returns:
        str: Formatted time string.
    """
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e12:
                dt = datetime.fromtimestamp(ts / 1e9)
            else:
                dt = datetime.fromtimestamp(ts)
            return dt.strftime("%H:%M:%S")
        elif isinstance(ts, str):
            return ts
        else:
            return datetime.now().strftime("%H:%M:%S")
    except:
        return datetime.now().strftime("%H:%M:%S")


def show_wab_status():
    """
    Shows W&B connection status in sidebar
    """
    if "wab_api" in st.session_state and st.session_state.wab_api is not None:
        st.sidebar.success("W&B Connected")
        
        if "last_wab_fetch_time" in st.session_state and st.session_state.last_wab_fetch_time > 0:
            time_since_fetch = time.time() - st.session_state.last_wab_fetch_time
            
            if "last_wab_step" in st.session_state and st.session_state.last_wab_step >= 0:
                st.sidebar.info(
                    f"Last data: step {st.session_state.last_wab_step}\n\n"
                    f"Checked {int(time_since_fetch)}s ago"
                )
            else:
                st.sidebar.info(f"Last check: {int(time_since_fetch)}s ago")
    else:
        st.sidebar.error("W&B Not Connected")