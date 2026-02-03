# SARIMAX Energy Dashboard

A comprehensive smart energy consumption monitoring and forecasting dashboard. Built with a focus on predictive analytics using SARIMAX time series models and automated notifications via Gmail OAuth2.

## 📁 Project Structure

```text
Sarimax-Thesis/
├── collector/               # LIVE Data Collection Pipeline (Dockerized)
│   ├── storage/             # MongoDB Client & Schemas
│   ├── utils/               # Data Normalizers & Historical Backfillers
│   └── data_collector.py    # Main 10-minute interval engine
├── api/                     # Python Forecast API (FastAPI)
│   ├── index.py             # Entry point
│   └── utils/               # Email & Forecast utilities
├── src/                     # React Frontend Dashboard
├── data/                    # Local CSV energy logs
├── Dockerfile               # Containerization for collector
├── docker-compose.yml       # Orchestration for cloud deployment
└── .env                     # Credentials & API Keys
```

## 🚀 Data Pipeline (Dockerized)

The energy data is managed by a modular collection pipeline that ensures high-fidelity datasets:

- **Live Collection**: Fetches real-time Volts, Amps, and Watts from Tuya devices every 10 minutes.
- **Strict Alignment**: Automatically aligns data to exactly **144 points per day** (:00, :10, :20...).
- **Historical Consistency**: A dedicated historical management system ensures that previous days are complete, with full support for centivolt/deciwatt normalization.
- **Cloud Ready**: Optimized for lightweight Linux VMs (Azure/AWS) using Docker and Swap optimization.

## 🚀 Getting Started

You can run this project either using **Docker** (recommended) or **Manually**.

### Option A: Docker Setup (Fastest)
This starts the Data Collector and the Forecast API in the background.
```bash
# 1. Clone & Enter
git clone https://github.com/geovportodo14/Sarimax-Thesis.git
cd Sarimax-Thesis

# 2. Setup .env
# Create a .env file and paste the credentials provided in the walkthrough.

# 3. Launch Services
docker-compose up --build -d

# 4. Start Frontend (on your host machine)
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
uvicorn api.index:app --reload
```
#### 3. Data Collector
```bash
python collector/data_collector.py
```

## 📊 Historical Dataset
The project maintains a high-quality dataset starting from **January 3rd**, categorized into:
- **Baseline Period**: High-resolution logs capturing appliance behaviors.
- **Monitoring Period**: Live synchronized data streamed to MongoDB Atlas.
- **Data Format**: Standardized units (**V, A, W, kWh**) for seamless integration with SARIMAX modeling.

## 📧 Gmail Notifications
Automated notifications are sent via Gmail OAuth2:
1.  **Welcome Emails**: Sent upon successful connection.
2.  **Budget Alerts**: Triggered when consumption exceeds predicted SARIMAX thresholds.

## ☁️ Deployment
- **Collector & API**: Deployed on Azure VM via Docker Compose.
- **Frontend**: Deployed on Vercel for fast global access.
- **Database**: Hosted on MongoDB Atlas.

## 📄 License
MIT - Part of the TH1 SARIMAX V2 Thesis Project.
