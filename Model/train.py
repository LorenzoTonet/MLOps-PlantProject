from Model.model import prepare_data, train
import pandas as pd
import wandb


'''
This script is the main entry point for training and saving the N-HITS model. 
It loads the dataset, prepares it, trains the model, and saves it to Weights & Biases for future use.
Every function used here is defined in model.py.
'''


if __name__ == "__main__":

    # load dataset from W&B current running run
    api = wandb.Api()
    runs = api.runs("MLOps-PlantProject/sensor-read-test", filters={"state": "running"})
    if not runs:
        raise Exception("No running W&B run found in the specified project.")
    
    latest_run = runs[0]
    history_list = latest_run.scan_history()
    stats_df = pd.DataFrame([row for row in history_list])

    # prepare data
    df = prepare_data(stats_df)
    # train
    model, mae = train(df)
    print('\n\n')
    print('Model:\n', model)
    print('\n')
    print('MAE:\n', mae)
    print('\n')
    print("Training complete. Model saved.\n")
