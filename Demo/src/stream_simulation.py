import csv
from datetime import datetime

# -----------------------------
# Simulate a data stream from a CSV file
# -----------------------------

def sensor_data_generator(csv_path):
    """
    Generator that yields sensor data dictionaries from a CSV file.
    Args:
        csv_path (str): Path to the CSV file.
    Yields:
        dict: A dictionary containing sensor data for a plant.
    """
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            plant_id = int(float(row["plant_id"]))

            yield {
                "plant": f"plant_{plant_id}",
                "timestamp": datetime.fromtimestamp(
                    int(row["timestamp"]) / 1e9
                ).strftime("%H:%M:%S"),

                "light": float(row["light_value"]),
                "light_sd": float(row["light_w_sd"]),

                "temperature": float(row["temp_value"]),
                "temperature_sd": float(row["temp_w_sd"]),

                "humidity": float(row["humid_value"]),
                "humidity_sd": float(row["humid_w_sd"]),

                "water": float(row["water_value"]),
                "water_sd": float(row["water_w_sd"]),
            }
