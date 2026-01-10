<<<<<<< HEAD
# SARIMAX Energy Dashboard

A React.js dashboard for energy consumption forecasting with interactive charts and controls.

## Features

- **Actual vs Forecast Chart**: Line chart showing actual energy consumption vs forecasted values
- **Previous vs Forecasted Chart**: Bar chart comparing previous and forecasted consumption
- **Forecast Controls**: Adjustable history period, forecast period, tariff rate, and budget
- **Consumption Ranking**: Appliance-level consumption breakdown with kWh and PHP costs
- **Energy Forecast Summary**: Summary statistics including next period, previous period, actual usage, top appliance, and budget status

## Tech Stack

- **React 18**: UI framework
- **Tailwind CSS**: Styling
- **Chart.js + react-chartjs-2**: Charts
- **React Scripts**: Build tooling

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Project Structure

```
src/
├── components/
│   ├── DashboardHeader.js          # Dashboard header with date navigation
│   ├── ActualForecastChart.js      # Line chart for actual vs forecast
│   ├── PreviousForecastChart.js    # Bar chart for previous vs forecasted
│   ├── ForecastControls.js         # Control panel for forecast parameters
│   ├── ConsumptionRanking.js       # Appliance consumption ranking
│   └── EnergyForecastSummary.js    # Summary statistics card
├── App.js                          # Main application component
├── index.js                        # Application entry point
└── index.css                       # Global styles with Tailwind imports
```

## Troubleshooting

### Module Resolution Errors (isexe, etc.)

If you encounter module resolution errors after `npm install`, try:

1. **Clean install:**
   ```bash
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

2. **OneDrive Sync Issues:**
   If your project is in OneDrive, it may interfere with `node_modules`. Consider:
   - Excluding `node_modules` from OneDrive sync (Right-click folder → OneDrive → Free up space)
   - Moving the project outside OneDrive for development
   - Using `.onedrivesyncignore` if supported

### Port Already in Use

If port 3000 is already in use:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Then restart npm start
```

## License

MIT

=======
# Thesis
Smart Energy Consumption Monitoring
>>>>>>> ec1311cb222add6e7ddc72458c600df1b28049ee
