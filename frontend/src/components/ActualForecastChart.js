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
import { Card, CardBody, SectionHeader, ChartLegend } from './ui';

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

// Chart color tokens (matching tailwind.config.js)
const CHART_COLORS = {
  actual: '#0EA5E9',      // Sky
  forecast: '#F59E0B',    // Amber
  healthy: '#10B981',     // Green
  atRisk: '#EF4444',      // Red
  stable: '#6B7280',      // Gray
};

const FONT_FAMILY = "'IBM Plex Sans', sans-serif";

function ActualForecastChart({
  labels,
  actualData,
  forecastData,
  allTime,
  onAllTimeChange,
  budgetThreshold = null,  // Optional threshold to show at-risk zones
  riskStatus = 'OK'        // 'OK' or 'At-Risk'
}) {
  // Determine if any forecast points exceed a threshold (risk visualization)
  const hasRiskData = riskStatus === 'At-Risk';

  const chartData = useMemo(() => ({
    labels: labels,
    datasets: [
      {
        label: 'Actual',
        data: actualData,
        borderColor: CHART_COLORS.actual,
        backgroundColor: (context) => {
          if (!context.chart.chartArea) return 'rgba(14, 165, 233, 0.08)';
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
          gradient.addColorStop(0, 'rgba(14, 165, 233, 0.16)');
          gradient.addColorStop(1, 'rgba(14, 165, 233, 0.02)');
          return gradient;
        },
        borderWidth: 2.5,
        pointBackgroundColor: CHART_COLORS.actual,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: CHART_COLORS.actual,
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 2,
        fill: true,
        tension: 0.35,
        order: 1,
      },
      {
        label: 'Forecast',
        data: forecastData,
        borderColor: CHART_COLORS.forecast,
        backgroundColor: (context) => {
          if (!context.chart.chartArea) return 'rgba(245, 158, 11, 0.08)';
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
          gradient.addColorStop(0, 'rgba(245, 158, 11, 0.18)');
          gradient.addColorStop(1, 'rgba(245, 158, 11, 0.03)');
          return gradient;
        },
        borderWidth: 2.5,
        borderDash: [6, 4],
        pointBackgroundColor: CHART_COLORS.forecast,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: CHART_COLORS.forecast,
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 2,
        fill: true,
        tension: 0.35,
        order: 2,
      },
    ],
  }), [labels, actualData, forecastData]);

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
        display: false, // We use custom legend
      },
      tooltip: {
        backgroundColor: 'rgba(23, 23, 23, 0.95)',
        padding: { x: 14, y: 10 },
        titleFont: {
          size: 13,
          weight: '600',
          family: FONT_FAMILY,
        },
        bodyFont: {
          size: 12,
          family: FONT_FAMILY,
        },
        titleColor: '#ffffff',
        bodyColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 10,
        displayColors: true,
        boxPadding: 4,
        callbacks: {
          title: function (context) {
            return context[0].label;
          },
          label: function (context) {
            const value = context.parsed.y;
            if (value === null) return null;
            return ` ${context.dataset.label}: ${value.toFixed(2)} kWh`;
          },
          afterBody: function (context) {
            // Add status indicator in tooltip
            const forecastValue = context.find(c => c.dataset.label === 'Forecast')?.parsed.y;
            if (forecastValue !== null && forecastValue !== undefined && budgetThreshold) {
              const status = forecastValue > budgetThreshold ? 'At Risk' : 'Healthy';
              return [`\n Status: ${status}`];
            }
            return [];
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.04)',
          drawBorder: false,
        },
        border: {
          display: false,
        },
        ticks: {
          color: '#737373',
          font: {
            size: 11,
            family: FONT_FAMILY,
          },
          maxRotation: 45,
          minRotation: 45,
          autoSkip: true,
          maxTicksLimit: 8,
          padding: 8,
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.04)',
          drawBorder: false,
        },
        border: {
          display: false,
        },
        beginAtZero: true,
        ticks: {
          color: '#737373',
          font: {
            size: 11,
            family: FONT_FAMILY,
          },
          padding: 12,
          callback: function (value) {
            return value.toFixed(1) + ' kWh';
          },
        },
      },
    },
  }), [budgetThreshold]);

  // Legend items
  const legendItems = [
    { color: CHART_COLORS.actual, label: 'Actual Consumption' },
    { color: CHART_COLORS.forecast, label: 'Forecast', dashed: true },
  ];

  // If showing risk status, add legend items
  if (hasRiskData) {
    legendItems.push({ color: CHART_COLORS.atRisk, label: 'At Risk' });
  }

  return (
    <Card className="h-full">
      <CardBody>
        <SectionHeader
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
          title="Actual vs Forecast"
          subtitle="Total energy consumption comparison"
          action={
            <div className="flex items-center gap-3 flex-wrap">
              {/* All-time toggle */}
              <div className="flex items-center gap-2 bg-surface-50 rounded-lg px-3 py-2 border border-surface-100">
                <span className="text-body-sm font-medium text-surface-600">All-time</span>
                <button
                  onClick={() => onAllTimeChange(!allTime)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 ${allTime ? 'bg-primary-600' : 'bg-surface-300'
                    }`}
                  role="switch"
                  aria-checked={allTime}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${allTime ? 'translate-x-6' : 'translate-x-1'
                      }`}
                  />
                </button>
              </div>
            </div>
          }
        />

        {/* Status indicator if at risk */}
        {hasRiskData && (
          <div className="flex items-center gap-2 mb-4 p-3 bg-red-50 border border-red-100 rounded-xl">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse-soft" />
            <span className="text-body-sm font-medium text-red-700">
              Forecast exceeds budget threshold
            </span>
          </div>
        )}

        {/* Chart */}
        <div className="h-[280px] sm:h-[320px]">
          <Line data={chartData} options={options} />
        </div>

        {/* Custom Legend */}
        <ChartLegend items={legendItems} />
      </CardBody>
    </Card>
  );
}

export default ActualForecastChart;
