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
import { Card, CardBody, SectionHeader, ChartLegend } from './ui';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Chart color tokens
const CHART_COLORS = {
  actual: '#0EA5E9',      // Sky - Actual/Previous
  forecast: '#F59E0B',    // Amber - Forecast
  healthy: '#10B981',     // Green
  atRisk: '#EF4444',      // Red
};

const FONT_FAMILY = "'IBM Plex Sans', sans-serif";

function PreviousForecastChart({ previousValue, forecastValue, budgetThreshold = null }) {
  // Determine if forecast exceeds threshold (at risk)
  const isForecastAtRisk = budgetThreshold && forecastValue > budgetThreshold;
  
  const chartData = useMemo(() => ({
    labels: ['Previous Period', 'Forecast'],
    datasets: [
      {
        label: 'Usage (kWh)',
        data: [previousValue, forecastValue],
        backgroundColor: (context) => {
          if (!context.chart.chartArea) {
            return context.dataIndex === 0 ? CHART_COLORS.actual : CHART_COLORS.forecast;
          }
          const ctx = context.chart.ctx;
          const chartArea = context.chart.chartArea;
          const index = context.dataIndex;
          
          if (index === 0) {
            // Previous - Blue gradient
            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, CHART_COLORS.actual);
            gradient.addColorStop(1, '#0284C7');
            return gradient;
          } else {
            // Forecast - Amber or Red if at risk
            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            if (isForecastAtRisk) {
              gradient.addColorStop(0, CHART_COLORS.atRisk);
              gradient.addColorStop(1, '#DC2626');
            } else {
              gradient.addColorStop(0, CHART_COLORS.forecast);
              gradient.addColorStop(1, '#D97706');
            }
            return gradient;
          }
        },
        borderRadius: 10,
        borderSkipped: false,
        barThickness: 48,
        maxBarThickness: 64,
      },
    ],
  }), [previousValue, forecastValue, isForecastAtRisk]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
        callbacks: {
          label: function(context) {
            return ` ${context.label}: ${context.parsed.y.toFixed(2)} kWh`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
        ticks: {
          color: '#525252',
          font: {
            size: 12,
            weight: '500',
            family: FONT_FAMILY,
          },
          padding: 8,
        },
      },
      y: {
        beginAtZero: true,
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
          padding: 12,
          callback: function(value) {
            return value.toFixed(1) + ' kWh';
          },
        },
      },
    },
  }), []);

  // Comparison stats
  const difference = forecastValue - previousValue;
  const percentChange = previousValue > 0 ? ((difference / previousValue) * 100) : 0;
  const isIncrease = difference > 0;

  // Legend items
  const legendItems = [
    { color: CHART_COLORS.actual, label: 'Previous Period' },
    { color: isForecastAtRisk ? CHART_COLORS.atRisk : CHART_COLORS.forecast, label: isForecastAtRisk ? 'Forecast (At Risk)' : 'Forecast' },
  ];

  return (
    <Card className="h-full">
      <CardBody>
        <SectionHeader
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          }
          title="Period Comparison"
          subtitle="Previous vs forecasted usage"
        />

        {/* Quick stats */}
        <div className="flex items-center gap-4 mb-5 p-3 bg-surface-50 rounded-xl border border-surface-100">
          <div className="flex-1">
            <p className="text-caption text-surface-500 mb-0.5">Difference</p>
            <p className={`text-body-md font-semibold tabular-nums ${isIncrease ? 'text-red-600' : 'text-emerald-600'}`}>
              {isIncrease ? '+' : ''}{difference.toFixed(2)} kWh
            </p>
          </div>
          <div className="w-px h-8 bg-surface-200" />
          <div className="flex-1">
            <p className="text-caption text-surface-500 mb-0.5">Change</p>
            <div className="flex items-center gap-1.5">
              <span className={`text-body-md font-semibold tabular-nums ${isIncrease ? 'text-red-600' : 'text-emerald-600'}`}>
                {isIncrease ? '+' : ''}{percentChange.toFixed(1)}%
              </span>
              {isIncrease ? (
                <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              )}
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-[200px] sm:h-[220px]">
          <Bar data={chartData} options={options} />
        </div>

        {/* Custom Legend */}
        <ChartLegend items={legendItems} />
      </CardBody>
    </Card>
  );
}

export default PreviousForecastChart;
