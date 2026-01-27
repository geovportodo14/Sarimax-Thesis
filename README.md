# SARIMAX Energy Dashboard

A project for smart energy consumption monitoring and forecasting using SARIMAX time series analysis and TimeGAN models.

## 📁 Project Structure

```text
Sarimax-Thesis/
├── frontend/                # React application
│   ├── public/              # Static files
│   ├── src/                 # React source code
│   ├── package.json         # Frontend dependencies
│   └── ...
├── backend/                 # Python logic & core scripts
│   ├── collection/          # Data collection scripts (Tuya IoT)
│   ├── models/              # ML models (GAN, SARIMAX)
│   ├── utils/               # Diagnostics and helper scripts
│   └── tests/               # Verification and test scripts
├── data/                    # Centralized data storage
│   ├── energy_data/         # Original energy dataset
│   └── logs/                # CSV log files
├── .gitignore
├── requirements.txt         # Consolidated Python dependencies
└── README.md                # This file
```

## 📦 Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The app will automatically open at [http://localhost:3000](http://localhost:3000)

## 🐍 Backend / Data Collection

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run data collection:**
   ```bash
   # From the root directory
   python backend/collection/tuyaandweather.py
   ```

3. **Run model validation:**
   ```bash
   python backend/tests/verify_stage4_generation.py
   ```

## 📄 License
MIT

## 👥 Contributors
Thesis Project - Smart Energy Consumption Monitoring

