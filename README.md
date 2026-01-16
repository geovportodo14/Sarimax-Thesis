# SARIMAX Energy Dashboard

A React.js dashboard for smart energy consumption monitoring and forecasting using SARIMAX time series analysis.

## 🎯 Features

- **Actual vs Forecast Chart**: Interactive line chart showing actual energy consumption vs forecasted values
- **Previous vs Forecasted Chart**: Bar chart comparing previous and forecasted consumption
- **Forecast Controls**: Adjustable parameters including history period, forecast period, tariff rate, and budget
- **Consumption Ranking**: Appliance-level consumption breakdown with kWh usage and PHP costs
- **Energy Forecast Summary**: Summary statistics including next period forecast, previous period comparison, actual usage, top consuming appliance, and budget status

## 🛠️ Tech Stack

- **React 18**: UI framework
- **Tailwind CSS**: Modern utility-first CSS framework
- **Chart.js + react-chartjs-2**: Interactive data visualization
- **React Scripts**: Build tooling and development server

## 📦 Frontend Setup

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Sarimax-Thesis
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

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder, ready for deployment.

## 📁 Project Structure

```
Sarimax-Thesis/
├── public/                          # Static files
├── src/
│   ├── components/
│   │   ├── DashboardHeader.js       # Header with date navigation
│   │   ├── ActualForecastChart.js   # Line chart component
│   │   ├── PreviousForecastChart.js # Bar chart component
│   │   ├── ForecastControls.js      # Forecast parameter controls
│   │   ├── ConsumptionRanking.js    # Appliance ranking table
│   │   └── EnergyForecastSummary.js # Summary statistics card
│   ├── App.js                       # Main application component
│   ├── index.js                     # Application entry point
│   └── index.css                    # Global styles + Tailwind imports
├── package.json                     # Frontend dependencies
└── README.md                        # This file
```

## 🐛 Troubleshooting

### npm install fails

If you encounter errors during `npm install`:

1. **Clean install:**
   ```bash
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

2. **Check Node version:**
   ```bash
   node --version  # Should be v14+
   npm --version   # Should be v6+
   ```

### Port 3000 already in use

**On macOS/Linux:**
```bash
lsof -ti:3000 | xargs kill -9
```

**On Windows:**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

Then restart:
```bash
npm start
```

## 🐍 Backend / Data Collection (Optional)

This repository also includes Python scripts for collecting energy data from Tuya IoT devices. These are **not required** to run the React dashboard.

If you want to run the data collection scripts:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run data collection:**
   ```bash
   python tuyaandweather.py
   # or
   python Data_Colletion.py
   ```

## 📄 License

MIT

## 👥 Contributors

Thesis Project - Smart Energy Consumption Monitoring
