# ⚡ SARIMAX Energy Dashboard

A comprehensive smart energy consumption monitoring and forecasting dashboard. Built with a focus on predictive analytics using SARIMAX time series models, fully automated data pipelines, and intelligent notifications via Gmail OAuth2.

## 📁 Project Structure

The project follows a "Hybrid Clean" architecture, grouping backend logic while keeping the frontend accessible for easy builds.

```text
Sarimax-Thesis/
├── backend/
│   ├── api/                 # FastAPI Forecast Server
│   │   └── index.py         # Entry point & SARIMAX logic
│   ├── collector/           # LIVE IoT Data Ingestion
│   │   ├── storage/         # MongoDB Client & Schemas
│   │   └── data_collector.py # 24/7 Engine & Backfill Logic
│   └── preprocessing/       # TH2 Automated Pipeline
│       ├── TH2_Pipeline_Runner.py  # Master Orchestrator
│       ├── TH2_Mongo_Extractor.py  # Cloud Data Fetcher
│       └── stage_*.py              # Stages A-D (Standardize, Clean, Features, Export)
├── src/                     # React Frontend Dashboard
├── data/                    # Data Storage
│   ├── raw/                 # Fresh from MongoDB Atlas
│   ├── intermediate/        # Pipeline Processing Cache
│   ├── final/               # Modeling-Ready Datasets (Ready for SARIMAX)
│   └── archive/             # Historical logs
├── docs/                    # Thesis Documentation & Analysis
├── main.py                  # UNIFIED ENTRY POINT (Local Dev)
├── deploy.sh                # Azure VM Auto-Deployment Script
├── Dockerfile               # Production Container
└── docker-compose.yml       # Service Orchestration
```

## 🔄 The Automated Workflow

Our backend is designed to run autonomously, handling everything from data outages to model preparation without human intervention.

### 1. Smart Collection & Backfilling 🛡️
- **Engine**: `data_collector.py`
- **Function**: Polls Tuya Smart Plugs every 10 minutes.
- **Safety Net**: If the system goes offline (e.g., power outage), it automatically "backfills" missing historical data from the Tuya Cloud upon restart or every midnight.

### 2. Auto-Triggered Preprocessing 🧠
- **Engine**: `TH2_Pipeline_Runner.py`
- **Trigger**: Runs automatically every day at 12:00 AM (midnight) or manual trigger.
- **Process**:
    1.  **Extraction**: Pulls verified data from MongoDB.
    2.  **Stage A**: Standardizes units and timestamps (UTC+8).
    3.  **Stage B**: Cleans energy data and handles power spikes.
    4.  **Stage C**: Computes SARIMAX features (Lags, Rolling Means).
    5.  **Stage D**: Exports `model_ready_*.csv` to `data/final/`.

### 3. Forecasting API 🔮
- **Engine**: FastAPI (`backend/api/index.py`)
- **Function**: Consumes the `data/final/` datasets to serve real-time consumption forecasts and budget alerts.

## � Getting Started

You can run the entire system in two ways.

### Option A: Docker (Recommended) 🐳
The easiest way. No Python installation required.

```bash
# Start Backend Services (Collector + API)
docker-compose up --build -d

# Start Frontend (Host)
npm install && npm start
```

### Option B: Local Python (Manual) 🐍
For development or debugging.

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Unified Orchestrator (Starts API + Collector)
python main.py

# 3. Start Frontend (Separate Terminal)
npm start
```

## ☁️ Deployment (Azure VM)

To update the live server:
1.  SHH into the VM.
2.  Run the auto-deploy script:
    ```bash
    git pull
    ./deploy.sh
    ```
    *(This script handles stopping containers, rebuilding, and cleaning up.)*

## 📧 Gmail Notifications
Automated notifications are sent via Gmail OAuth2:
1.  **Welcome Emails**: Sent upon successful connection.
2.  **Budget Alerts**: Triggered when consumption exceeds predicted SARIMAX thresholds.

## 📄 License
MIT - Part of the TH1 SARIMAX V2 Thesis Project.
