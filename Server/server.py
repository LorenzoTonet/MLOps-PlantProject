from pathlib import Path
from datetime import datetime
import traceback
import json
import random
import os
import wandb
import serial
import serial.tools.list_ports
import threading
import queue
import time

# Main variables configuration

PROJECT_NAME = "sensor-read-test"
ENTITY = "MLOps-PlantProject"
RUN_NAME = f"run-{datetime.now():%Y%m%d-%H%M%S}"
DATA_DIR = Path("./data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
BAUDRATE = 115200

# Reads from the board


def read_data(s0):

    vals = list(
        map(float,
            s0[2:].replace("'", "").replace("\\r\\n", "").split(',')))

    res = {
        "timestamp": time.time_ns(),

        "plant_id": vals[0],

        "light_value":  vals[1],
        "light_w_mean": vals[2],
        "light_w_sd":   vals[3],
        "light_w_max":  vals[4],
        "light_w_min":  vals[5],

        "temp_value":   vals[6],
        "temp_w_mean":  vals[7],
        "temp_w_sd":    vals[8],
        "temp_w_max":   vals[9],
        "temp_w_min":   vals[10],

        "humid_value":  vals[11],
        "humid_w_mean": vals[12],
        "humid_w_sd":   vals[13],
        "humid_w_max":  vals[14],
        "humid_w_min":  vals[15],

        "water_value":  vals[16],
        "water_w_mean": vals[17],
        "water_w_sd":   vals[18],
        "water_w_max":  vals[19],
        "water_w_min":  vals[20]
    }

    return res

# Manages async reads from the board


def dict_to_string(dct: dict, header=False):
    if header:
        return ', '.join([f"{key}" for key in dct.keys()]) + "\n"
    else:
        return ', '.join([f"{dct[key]}" for key in dct.keys()]) + "\n"


class SerialManager:

    def __init__(self, port, baudrate=BAUDRATE):
        self.serial = serial.Serial(port, baudrate)
        self.read_queue = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        self.read_thread = threading.Thread(target=self._reader)
        self.read_thread.daemon = True
        self.read_thread.start()

    def _reader(self):
        while self.running:
            if self.serial.in_waiting:
                time.sleep(0.5)
                data = self.serial.read(self.serial.in_waiting)
                self.read_queue.put(data)
            time.sleep(0.001)

    def receive(self, timeout=None):
        return self.read_queue.get(timeout=timeout)

    def stop(self):
        self.running = False
        self.read_thread.join()
        self.serial.close()


def main():

    # Find port where an arduino is currently running
    ports = serial.tools.list_ports.comports()
    dev_port = None
    for port in ports:
        if port.manufacturer is not None:
            if "Arduino" in port.manufacturer:
                dev_port = port.device

    if dev_port is None:
        raise AssertionError("No Board is currently connected.")

    # Connect to W&B under a new run
    # wandb.init(
    #     project=PROJECT_NAME,
    #     entity=ENTITY,
    #     name=RUN_NAME,
    #     reinit=False,
    # )

    # Initialize Serial Manager class and
    # configure local logging folder
    manager = SerialManager(dev_port, BAUDRATE)
    manager.start()
    csv_path = DATA_DIR/f"{RUN_NAME}.csv"

    first_write = True

    # Loop!
    try:
        while True:

            # Try to obtain a response from the SerialManager
            try:
                byte_sample = manager.receive(timeout=5.0)
                sample = read_data(str(byte_sample))
                print(sample)

            # If not found anything continue until the next loop
            except queue.Empty:
                continue

            # In case of exception close the writer and terminate
            # the current running run
            except Exception as exc:
                print(f"Terminating with exception {exc}")
                manager.stop()
                # wandb.finish()
                break

            # Log scalar metrics to W&B
            # wandb.log(sample)

            # Local CSV write
            with open(csv_path, "a") as f:
                if first_write:
                    f.write(dict_to_string(sample, header=True))
                    first_write = False
                f.write(dict_to_string(sample))

            # Wait a small delay before checking
            # if new data has arrived
            time.sleep(0.1)

    except Exception as exc:
        manager.stop()
        # wandb.finish()
        print(f"Terminating with exception {exc}")


if __name__ == "__main__":
    main()

# Nothing else going on here
