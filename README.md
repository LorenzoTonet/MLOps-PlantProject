# PlantMo

## Overview
This project addresses the challenge of reactive plant care by developing an automated smart monitoring system. The system's scope encompasses the collection, aggregation, and continuous analysis of environmental data from four sensor types: light, temperature, humidity, and soil moisture, to enable data-driven decision-making and real-time visual-ization. It explicitly excludes direct physical interventions such as automated watering or climate control.
The primary objectives are to design a reliable monitoring infrastructure that supports drift detection and the identification of anomalous environmental trends. System effec-tiveness will be measured through key performance indicators including Data Availability, Data Latency, System Reliability, Drift Detection Accuracy, and Dashboard Responsive-ness. This initiative is relevant because it fundamentally transforms plant cultivation from a manual, snapshot-based approach into a proactive, insight-driven practice. By delivering continuous monitoring and early warning capabilities, the system empowers users to maintain optimal growing conditions and implement timely interventions before environmental issues compromise plant conditions.

## Key Features
- Monitoring of plant's environmental conditions.
- Machine Learning kernel to predict watering necessities.
- Detection of drifts in environment conditions (e.g. change of season, sensors failures...)
- Customizable plant monitoring conditions (e.g. minimum light, maximum temperature)
  
## Dashboard
<img width="1280" height="584" alt="image" src="https://github.com/user-attachments/assets/1babd03c-c980-4c2e-b678-0ad8c1cb43e1" />

### Real-time Monitoring Dashboard
Interactive dashboard for visualizing plant conditions.

| Run locally: `streamlit run executable.py`

**Features:**
- Data buffering
- Real-time data monitoring
- Multiple plant management
- Synthetic data generation for test and debug purposes

### ML Model Monitoring
The model registry is implemented using Weights & Biases (W&B), which provides integrated experiment tracking and model versioning capabilities. Each trained model is stored as a distinct artifact, uniquely associated with its version, configuration, and training context. Models are saved as immutable versions, ensuring that previously validated models remain accessible and unchanged.
**Features:**
- Save different model versions
- Track performances
- Have a comparison between different models
- Track retrains

### Cloud data storage
The application is fully integrated with Weights and Biases application used to communicate with the local server and store real-time data.

## Architecture
<img width="2560" height="2190" alt="image" src="https://github.com/user-attachments/assets/d78bf3fb-d0e1-4cce-869f-6284c6a2d42f" />

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
```bash
cd Board
make install-core
make
```

### Quick Start
1. **Install the circuit-board in your greenhouse and follow "Installation instructions"**
   
3. **Create a W&B API-Key and update api_key.json** (if not already done)

4. **Launch the dashboard**:
   ```bash
   streamlit run executable.py
   ```

5. **Add your plants, customize threshold values, set your ideal update time and the number of data-points to visualize** (can be easily done frome the sideboard!):
<p align="center">
  <img src="https://github.com/user-attachments/assets/80d47b29-adc4-40bc-8b14-3ea374643f34" width="270" />
  <img src="https://github.com/user-attachments/assets/684f479c-1e26-46c8-b6d3-9ef7706bf4ea" width="270" />
  <img src="https://github.com/user-attachments/assets/3f7be83e-9a26-4689-bfda-668072a2a2da" width="270" />
</p>


5. **Take care of your plants!**

## Documentation

1. **System Specification Document (SSD)**
   - Problem definition
   - Data specifications
   - Functional requirements
   - Non functional requirements
   - Project architecture
   - Risk analysis
2. **Project Proposal and Developement Plan**
   - Deliverables
   - Milestones
   - WBS
   - Sprint Plan
   - DoD/DoR
   - Resources and infrastructure
3. **Operational Governance and Versioning Document**
   - Version control strategy
   - CI/CD reference
   - Model lifecycle governance
   - Monitoring and maintenance plan
## License

This project is open source and available for educational and research purposes.
