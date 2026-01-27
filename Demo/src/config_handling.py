import json
from pathlib import Path
import streamlit as st

# -----------------------------
# CONFIG HANDLING
# -----------------------------

def load_config(CONFIG_FILE):
    """
    Load configuration from a JSON file.
    Args:
        CONFIG_FILE (Path): Path to the configuration file.
    Returns:
        dict: Configuration data if file exists, else None.
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
        
def save_config(CONFIG_FILE):
    """
    Save configuration to a JSON file.
    Args:
        CONFIG_FILE (Path): Path to the configuration file.
    """
    config = {
        "sensors": st.session_state.sensors,
        "plants": st.session_state.plants,
        "stdev_sensors": st.session_state.stdev_sensors,
        "thresholds": st.session_state.get("thresholds", {})
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_api_key(api_key_file="api_key.json"):
    """
    Load W&B API key from JSON file.
    
    Args:
        api_key_file (str): Path to the API key JSON file
        
    Returns:
        str: The W&B API key, or None if not found
    """
    api_key_path = Path(api_key_file)
    
    if not api_key_path.exists():
        return None
    
    try:
        with open(api_key_path, 'r') as f:
            data = json.load(f)
            return data.get("wandb_api_key")
    except Exception as e:
        print(f"Error loading API key: {e}")
        return None