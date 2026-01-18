import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function ActualForecastChart({ labels, actualData, forecastData, allTime, onAllTimeChange, selectedFilter, onFilterChange, applianceFilters = ['Electric Fan', 'Rice Cooker', 'Television'], customDatasets = null }) {
  const chartData = useMemo(() => {
    if (customDatasets) {
      return {
        labels: labels,
        datasets: customDatasets
      };
    }

    return {
      labels: labels,
      datasets: [
        {
          label: 'Actual',
          data: actualData,
          borderColor: '#3b82f6',
          backgroundColor: (context) => {
            if (!context.chart.chartArea) return 'rgba(59, 130, 246, 0.1)';
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)');
            return gradient;
          },
          borderWidth: 3,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointHoverBackgroundColor: '#2563eb',
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 2,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Forecast',
          data: forecastData,
          borderColor: '#f97316',
          backgroundColor: (context) => {
            if (!context.chart.chartArea) return 'rgba(249, 115, 22, 0.1)';
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
            gradient.addColorStop(0, 'rgba(249, 115, 22, 0.3)');
            gradient.addColorStop(1, 'rgba(249, 115, 22, 0.05)');
            return gradient;
          },
          borderWidth: 3,
          borderDash: [5, 5],
          pointBackgroundColor: '#f97316',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointHoverBackgroundColor: '#ea580c',
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 2,
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [labels, actualData, forecastData, customDatasets]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    spanGaps: true,
    interaction: {
      intersect: false,
      mode: 'index',
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 13,
        },
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} kWh`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 11,
          },
          autoSkip: false,
          maxRotation: 50,
          minRotation: 50,
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        beginAtZero: true,
        ticks: {
          color: '#6b7280',
          font: {
            size: 11,
          },
          callback: function (value) {
            return value + ' kWh';
          },
        },
      },
    },
  }), []);

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-8 h-full hover-lift animate-slide-up">
      <div className="flex justify-between items-start flex-wrap gap-4 mb-6">
        <div>
          <h4 className="text-2xl font-bold text-gray-800 m-0 mb-1 flex items-center gap-2">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Actual VS Forecast
          </h4>
          <p className="text-sm text-gray-500 mt-1">Energy consumption comparison</p>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2">
            <span className="text-sm font-medium text-gray-700">All-time</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={allTime}
                onChange={(e) => onAllTimeChange(e.target.checked)}
                className="sr-only peer"
              />
              <div className={`w-11 h-6 rounded-full transition-all duration-200 ${allTime ? 'bg-blue-600' : 'bg-gray-300'}`}>
                <div className={`absolute top-[2px] left-[2px] bg-white rounded-full h-5 w-5 shadow-md transition-transform duration-200 ${allTime ? 'translate-x-5' : 'translate-x-0'}`}></div>
              </div>
            </label>
          </div>

          <div className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span className="text-sm font-medium text-gray-700">Filter</span>
            <select
              value={selectedFilter}
              onChange={(e) => onFilterChange(e.target.value)}
              className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
            >
              {applianceFilters.map((appliance) => (
                <option key={appliance} value={appliance}>
                  {appliance}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="h-[300px] mt-2">
        <Line data={chartData} options={options} />
      </div>

      <div className="flex gap-8 mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-600 shadow-sm inline-block"></div>
          <span className="text-sm font-medium text-gray-700">Actual</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-orange-500 shadow-sm inline-block"></div>
          <span className="text-sm font-medium text-gray-700">Forecast</span>
        </div>
      </div>
    </div>
  );
}

export default ActualForecastChart;

