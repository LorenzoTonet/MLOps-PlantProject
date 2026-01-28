# PlantMo

## Overview

## Key Features

## Dashboards

### Real-time Monitoring Dashboard
Interactive dashboard for visualizing plant conditions.

| Run locally: `streamlit run executable.py`

**Features:**


### ML Model Monitoring

**Features:**


## Architecture


## Project Structure
```bash
    .
    ├── Board
    │   ├── main
    │   │   └── main.ino
    │   ├── info.md
    │   └── makefile
    ├── Data
    │   ├── dataset.py
    │   ├── info.md
    │   ├── __init__.py
    │   └── local_host_data.py
    ├── Demo
    │   ├── Data
    │   │   ├── plant_data_simulation.csv
    │   ├── src
    │   │   ├── config_handling.py
    │   │   ├── data_generators.py
    │   │   ├── plant_data_management.py
    │   │   ├── plotting_functions.py
    │   │   ├── stream_simulation.py
    │   │   └── wab_stream.py
    │   ├── application.py
    │   ├── greenhouse_info.json
    ├── Documents
    │   ├── info.md
    │   ├── Project_Proposal_Development_Plan_02.pdf
    │   └── System_Specification_Document_01.pdf
    ├── Model
    │   ├── info.md
    │   ├── model.py
    │   └── train.py
    ├── Server
    │   └── server.py
    ├── executable.py
    ├── api_key.json
    ├── README.md
    └── requirements.txt

```
## Getting Started

### Prerequisites

- Python 3.13+
- Arduino CLI
- Weights and Biases API-key

### Installation

```bash
git clone https://github.com/LorenzoTonet/MLOps-PlantMo.git
cd MLOps-PlantMo
pip install -r requirements.txt
```

### Quick Start

1. **Create a W&B API-Key and update api_key.json** (if not already done):

2. **Launch the dashboard**:
   ```bash
   streamlit run executable.py
   ```

3. **Add your plants, customize threshold values, set your ideal update time and the number of data-points to visualize** (can be easily done frome the sideboard!):
<p align="center">
  <img src="https://github.com/user-attachments/assets/80d47b29-adc4-40bc-8b14-3ea374643f34" width="270" />
  <img src="https://github.com/user-attachments/assets/684f479c-1e26-46c8-b6d3-9ef7706bf4ea" width="270" />
  <img src="https://github.com/user-attachments/assets/3f7be83e-9a26-4689-bfda-668072a2a2da" width="270" />
</p>


4. **Take care of your plants!**

## Documentation


## License

This project is open source and available for educational and research purposes.
