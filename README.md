# ⚡ SARIMAX Energy Dashboard

A comprehensive smart energy consumption monitoring and forecasting dashboard. Built with a focus on predictive analytics using SARIMAX time series models and automated notifications via Gmail OAuth2.

## 📁 Project Structure

```text
Sarimax-Thesis/
├── backend/
│   ├── collector/           # LIVE Data Collection Pipeline
│   │   ├── storage/         # MongoDB Client & Schemas
│   │   └── data_collector.py # Main 10-minute interval engine
│   ├── preprocessing/       # ML Data Pipeline (5 Phases)
│   │   ├── TH2_Pipeline_Runner.py # Main pipeline orchestrator
│   │   └── TH2_Mongo_Extractor.py # Data extraction from Atlas
│   └── api/                 # Python Forecast API (FastAPI)
│       └── index.py         # Entry point & SARIMAX logic
├── src/                     # React Frontend Dashboard
├── data/                    # Data Storage (Raw, Intermediate, Final)
├── logs/                    # Persistent logs for Docker services
├── Dockerfile               # Unified containerization
└── docker-compose.yml       # Service orchestration
```

## 🔄 The Entire Process

The project follows a rigorous data lifecycle from raw electrical signals to predictive insights:

### 1. Data Collection (Live)
- **Engine**: `data_collector.py` polls Tuya Smart Plugs every 10 minutes.
- **Alignment**: Automatically aligns data to exactly **144 points per day** (:00, :10, :20...).
- **Redundancy**: Stores data both in local CSV logs (`data/energy_data`) and MongoDB Atlas.
- **Backfill**: Automatically checks and fills gaps from the previous day every midnight.

### 2. Preprocessing Pipeline
The `TH2_Pipeline_Runner.py` orchestrates a 5-phase data refinement process:
- **Phase 0 (Extraction)**: Decouples raw data from MongoDB Atlas.
- **Stage A (Standardization)**: Normalizes centivolt/deciwatt units and verifies data integrity.
- **Stage B (Cleaning)**: Handles outliers and derives base energy metrics.
- **Stage C (Features)**: Constructs rolling averages, lag features, and weather-dependent variables.
- **Stage D (Export)**: Generates the final high-fidelity dataset ready for SARIMAX modeling.

### 3. API & Forecasting
- **Engine**: FastAPI backend serves real-time energy forecasts.
- **Model**: Leverages SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous factors) to predict consumption based on historical trends and external weather data.

## 📊 Monitoring & Logging

When running via Docker, you can monitor the health and activity of the services using:

```bash
# View live data collection logs
docker logs -f tuya-data-collector

# View API / Forecast request logs
docker logs -f sarimax-api
```
> [!TIP]
> Persistent logs are also stored in the host's `./logs/` directory for long-term auditing.

## 🚀 Getting Started

### Option A: Docker Setup (Recommended)
This starts the Data Collector and the Forecast API in the background.
```bash
# 1. Launch Services
docker-compose up --build -d

# 2. Start Frontend (on your host machine)
npm install
npm start
```

### Option B: Manual Setup (Development)
If you prefer to run services individually:

#### 1. Frontend (React)
```bash
npm install
npm start
```
#### 2. Forecast API (FastAPI)
```bash
pip install -r requirements.txt
uvicorn backend.api.index:app --reload
```
#### 3. Data Collector
```bash
python backend/collector/data_collector.py
```

## 📧 Gmail Notifications
Automated notifications are sent via Gmail OAuth2:
1.  **Welcome Emails**: Sent upon successful connection.
2.  **Budget Alerts**: Triggered when consumption exceeds predicted SARIMAX thresholds.

## 📄 License
MIT - Part of the TH1 SARIMAX V2 Thesis Project.
