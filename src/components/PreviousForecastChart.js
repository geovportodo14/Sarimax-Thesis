import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function PreviousForecastChart({ previousValue, forecastValue }) {
  const chartData = useMemo(() => ({
    labels: ['Previous', 'Forecast'],
    datasets: [
      {
        label: 'Usage (kWh)',
        data: [previousValue, forecastValue],
        backgroundColor: (context) => {
          if (!context.chart.chartArea) {
            return context.dataIndex === 0 ? '#10b981' : '#f97316';
          }
          const ctx = context.chart.ctx;
          const chartArea = context.chart.chartArea;
          const index = context.dataIndex;
          if (index === 0) {
            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, '#10b981');
            gradient.addColorStop(1, '#059669');
            return gradient;
          } else {
            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, '#f97316');
            gradient.addColorStop(1, '#ea580c');
            return gradient;
          }
        },
        borderRadius: 12,
        borderSkipped: false,
      },
    ],
  }), [previousValue, forecastValue]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
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
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.y.toFixed(2)} kWh`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 12,
            weight: '600',
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 11,
          },
          callback: function(value) {
            return value + ' kWh';
          },
        },
      },
    },
  }), []);

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-8 h-full hover-lift animate-slide-up">
      <div className="mb-6">
        <h4 className="text-2xl font-bold text-gray-800 m-0 mb-1 flex items-center gap-2">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Previous VS Forecasted
        </h4>
        <p className="text-sm text-gray-500 mt-1">Period comparison</p>
      </div>

      <div className="h-[280px] mt-4">
        <Bar data={chartData} options={options} />
      </div>

      <div className="flex gap-6 mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-green-500 to-green-600 shadow-sm inline-block"></div>
          <span className="text-sm font-medium text-gray-700">Previous</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 shadow-sm inline-block"></div>
          <span className="text-sm font-medium text-gray-700">Forecasted</span>
        </div>
      </div>
    </div>
  );
}

export default PreviousForecastChart;

