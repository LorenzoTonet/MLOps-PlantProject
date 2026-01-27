import wandb

'''
THE FILE IS NOT READY TO BE USED. FUTURE COMMITS WILL COME TO FIX IT.
'''

project = "MLOps-PlantProject/sensor-read-test"

wanted_keys = {
    "plant",
    "timestamp",
    "light_value", "light_w_sd",
    "temp_value", "temp_w_sd",
    "humid_value", "humid_w_sd",
    "water_value", "water_w_sd",
}


api = wandb.Api()

# Prende le run ordinate per data di creazione (più recente prima)
runs = api.runs(project, order="-created_at")
latest_run = runs[0]
print("Latest run id:", latest_run.id)

history = list(latest_run.scan_history(min_step=latest_run.lastHistoryStep))
last_record = history[-1] if history else None

filtered_last_row = {
    k: last_record[k]
    for k in wanted_keys
    if k in last_record
}

print(filtered_last_row)