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
import { Card, CardBody, ChartLegend } from './ui';

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

// Chart color tokens
const CHART_COLORS = {
  actual: '#0EA5E9',      // Sky
  forecast: '#F59E0B',    // Amber
  healthy: '#10B981',     // Green
  atRisk: '#EF4444',      // Red
};

// Appliance-specific colors
const APPLIANCE_COLORS = {
  'Electric Fan': { primary: '#14B8A6', secondary: '#0F766E' },       // Teal
  'Air Conditioner': { primary: '#0EA5E9', secondary: '#0284C7' },    // Sky
  'Refrigerator': { primary: '#F59E0B', secondary: '#D97706' },       // Amber
};

const FONT_FAMILY = "'IBM Plex Sans', sans-serif";

// Appliance icons
const APPLIANCE_ICONS = {
  'Electric Fan': (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  ),
  'Air Conditioner': (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  'Refrigerator': (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 10h16" />
    </svg>
  ),
};

function ApplianceChart({
  applianceName,
  labels,
  actualData,
  forecastData,
  kwh,
  cost,
  budgetStatus = 'OK'
}) {
  const colors = useMemo(() => APPLIANCE_COLORS[applianceName] || { primary: '#6B7280', secondary: '#4B5563' }, [applianceName]);
  const icon = APPLIANCE_ICONS[applianceName];

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
        borderWidth: 2,
        pointBackgroundColor: CHART_COLORS.actual,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: true,
        tension: 0.35,
        order: 1,
      },
      {
        label: 'Forecast',
        data: forecastData,
        borderColor: colors.primary,
        backgroundColor: (context) => {
          if (!context.chart.chartArea) return `${colors.primary}15`;
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
          gradient.addColorStop(0, `${colors.primary}25`);
          gradient.addColorStop(1, `${colors.primary}05`);
          return gradient;
        },
        borderWidth: 2,
        borderDash: [6, 4],
        pointBackgroundColor: colors.primary,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: true,
        tension: 0.35,
        order: 2,
      },
    ],
  }), [labels, actualData, forecastData, colors]);

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
        backgroundColor: 'rgba(23, 23, 23, 0.95)',
        padding: { x: 12, y: 8 },
        titleFont: {
          size: 12,
          weight: '600',
          family: FONT_FAMILY,
        },
        bodyFont: {
          size: 11,
          family: FONT_FAMILY,
        },
        titleColor: '#ffffff',
        bodyColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        boxPadding: 4,
        callbacks: {
          title: function (context) {
            return context[0].label;
          },
          label: function (context) {
            const value = context.parsed.y;
            if (value === null) return null;
            return ` ${context.dataset.label}: ${value.toFixed(3)} kWh`;
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
            size: 10,
            family: FONT_FAMILY,
          },
          maxRotation: 45,
          minRotation: 45,
          autoSkip: true,
          maxTicksLimit: 6,
          padding: 6,
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
            size: 10,
            family: FONT_FAMILY,
          },
          padding: 8,
          callback: function (value) {
            return value.toFixed(2);
          },
        },
      },
    },
  }), []);

  // Legend items
  const legendItems = [
    { color: CHART_COLORS.actual, label: 'Actual' },
    { color: colors.primary, label: 'Forecast', dashed: true },
  ];

  return (
    <Card className="h-full">
      <CardBody className="p-4 sm:p-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${colors.primary}15`, color: colors.primary }}
            >
              {icon}
            </div>
            <div>
              <h4 className="text-body-md font-semibold text-surface-800">{applianceName}</h4>
              <p className="text-caption text-surface-500">Energy consumption</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-heading-sm font-bold text-surface-900 tabular-nums">{kwh.toFixed(2)} kWh</p>
            <p className="text-caption text-surface-500">₱{cost.toFixed(2)}</p>
          </div>
        </div>

        {/* Chart */}
        <div className="h-[180px] sm:h-[200px]">
          <Line data={chartData} options={options} />
        </div>

        {/* Custom Legend */}
        <ChartLegend items={legendItems} className="mt-3 pt-3" />
      </CardBody>
    </Card>
  );
}

export default ApplianceChart;
