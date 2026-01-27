import streamlit as st
import random
import time

from datetime import datetime

# -----------------------------
# RANDOM DATA GENERATION
# -----------------------------

def generate_random_data(plant_name: str) -> dict:
    """
    Generate random sensor data for a plant.
    Args:
        plant_name (str): Name of the plant.
    Returns:
        dict: A dictionary containing random sensor data.
    """
    return {
        "plant_id": plant_name,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "light_w_mean": random.uniform(200, 800),
        "light_w_sd": random.uniform(5, 20),
        "temp_w_mean": random.uniform(18, 32),
        "temp_w_sd": random.uniform(1, 5),
        "humid_w_mean": random.uniform(40, 80),
        "humid_w_sd": random.uniform(2, 10),
        "water_w_mean": random.uniform(50, 90),
        "water_w_sd": random.uniform(3, 15),
    }


def random_data_generator():
    """
    Generator for random data for all plants.
    Yields:
        dict: A dictionary containing random sensor data for a plant.
        
    """
    
    while True:
        # Generate data for a random plant
        plant = random.choice(st.session_state.plants)
        yield generate_random_data(plant)

        time.sleep(0.5)

def generate_snapshot():
    """
    Generate a snapshot of random data for all plants.
    Returns:
        list: A list of dictionaries containing random sensor data for all plants.
    """

    return [
        {
        "plant_id": plant,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "light_w_mean": random.uniform(200, 800),
        "light_w_sd": random.uniform(5, 20),
        "temp_w_mean": random.uniform(18, 32),
        "temp_w_sd": random.uniform(1, 5),
        "humid_w_mean": random.uniform(40, 80),
        "humid_w_sd": random.uniform(2, 10),
        "water_w_mean": random.uniform(50, 90),
        "water_w_sd": random.uniform(3, 15),
    }
        for plant in st.session_state.plants
    ]
