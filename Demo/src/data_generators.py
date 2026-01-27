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
        "plant": plant_name,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "light": random.uniform(200, 800),
        "light_sd": random.uniform(5, 20),
        "temperature": random.uniform(18, 32),
        "temperature_sd": random.uniform(1, 5),
        "humidity": random.uniform(40, 80),
        "humidity_sd": random.uniform(2, 10),
        "water": random.uniform(50, 90),
        "water_sd": random.uniform(3, 15),
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
        "plant": plant,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "light": random.uniform(200, 800),
        "light_sd": random.uniform(5, 20),
        "temperature": random.uniform(18, 32),
        "temperature_sd": random.uniform(1, 5),
        "humidity": random.uniform(40, 80),
        "humidity_sd": random.uniform(2, 10),
        "water": random.uniform(50, 90),
        "water_sd": random.uniform(3, 15),
    }
        for plant in st.session_state.plants
    ]
