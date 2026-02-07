# ⚡ SARIMAX Energy Dashboard

A comprehensive smart energy consumption monitoring and forecasting dashboard. Built with a focus on predictive analytics using SARIMAX time series models, fully automated data pipelines, and intelligent notifications via Gmail OAuth2.

## 🏗️ Architecture: Separation of Concerns

To maximize reliability and iteration speed, the system is split into two specialized environments:

| Component | Environment | Responsibility |
| :--- | :--- | :--- |
| **Data Collector** | Azure VM (Docker) | 24/7 IoT polling and "Smart Backfilling" to ensure 100% data integrity. |
| **Preprocessing** | Local Mac | Data extraction (Atlas -> CSV), Feature Engineering, and Model Dataset preparation. |

---

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

---

## � The Automated Workflow

Our backend is designed to run autonomously, handling everything from data outages to model preparation.

### 1. Smart Collection & Backfilling 🛡️
*   **Engine**: `data_collector.py` (Runs in Docker on Azure)
*   **Function**: Polls Tuya Smart Plugs every 10 minutes.
*   **Safety Net**: If the system goes offline, it automatically performs a **"Smart Backfill"** of missing intervals from the Tuya Cloud upon restart or every midnight.

### 2. Preprocessing Pipeline (Model Ready) 🧠
*   **Engine**: `TH2_Pipeline_Runner.py` (Recommended to run locally on your Mac)
*   **Workflow**:
    1.  **Extraction**: Pulls real-time data from MongoDB Atlas to local CSV.
    2.  **Stage A**: Standardizes units and timestamps (UTC+8).
    3.  **Stage B**: Cleans energy data and derives net kWh.
    4.  **Stage C**: Computes SARIMAX features (Lags, Rolling Means) and merges Weather data.
    5.  **Stage D**: Exports `model_ready_*.csv` to `data/final/`.

### 3. Forecasting API 🔮
*   **Engine**: FastAPI (`backend/api/index.py`)
*   **Function**: Consumes the final datasets to serve real-time forecasts and budget alerts.

---

## 🚀 Getting Started

### Option A: Docker (Azure VM - Collection) 🐳
The primary way to run the 24/7 data collector.

```bash
# Start Backend Services (Collector + API)
docker-compose up --build -d
```

### Option B: Local Python (Mac/Manual - Preprocessing) 🐍
Best for iterating on your thesis models and processing the collected data.

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Preprocessing Pipeline
python3 backend/preprocessing/TH2_Pipeline_Runner.py

# 3. Start Frontend Dashboard
npm install && npm start
```

---

## 📊 Monitoring & Logs

Check if the Live Data Collection is working using these commands:

```bash
# View Data Collector Logs (Live stream)
docker logs -f tuya-data-collector

# View Forecast API Logs
docker logs -f sarimax-api
```

---

## ☁️ Deployment (Azure VM)

To update the live server after making changes:
1.  Push changes to GitHub from your Mac.
2.  SSH into the Azure VM.
3.  Execute:
    ```bash
    git pull origin main
    docker-compose up --build -d
    ```

---

## � Gmail Notifications
Automated notifications are sent via Gmail OAuth2:
- **Welcome Emails**: Sent upon successful connection.
- **Budget Alerts**: Triggered when consumption exceeds predicted SARIMAX thresholds.

---

## 📄 License
MIT - Part of the TH1 SARIMAX V2 Thesis Project.
