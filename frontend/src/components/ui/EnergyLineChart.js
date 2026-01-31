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
import { Card, CardBody, SectionHeader, ChartLegend } from './index';

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

const FONT_FAMILY = "'IBM Plex Sans', sans-serif";

export const CHART_COLORS = {
    actual: '#0EA5E9',      // Sky
    forecast: '#F59E0B',    // Amber
    healthy: '#10B981',     // Green
    atRisk: '#EF4444',      // Red
    stable: '#6B7280',      // Gray
};

function EnergyLineChart({
    title,
    subtitle,
    icon,
    labels,
    actualData,
    forecastData,
    forecastColor = CHART_COLORS.forecast,
    isDashed = true,
    riskStatus = 'OK',
    extraAction = null,
    unit = 'kWh',
    height = 320,
}) {
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
                fill: true,
                tension: 0.35,
                order: 1,
            },
            {
                label: 'Forecast',
                data: forecastData,
                borderColor: forecastColor,
                backgroundColor: (context) => {
                    if (!context.chart.chartArea) return `${forecastColor}15`;
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, context.chart.chartArea.top, 0, context.chart.chartArea.bottom);
                    gradient.addColorStop(0, `${forecastColor}25`);
                    gradient.addColorStop(1, `${forecastColor}05`);
                    return gradient;
                },
                borderWidth: 2.5,
                borderDash: isDashed ? [6, 4] : [],
                pointBackgroundColor: forecastColor,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.35,
                order: 2,
            },
        ],
    }), [labels, actualData, forecastData, forecastColor, isDashed]);

    const options = useMemo(() => ({
        responsive: true,
        maintainAspectRatio: false,
        spanGaps: true,
        interaction: {
            intersect: false,
            mode: 'index',
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(23, 23, 23, 0.95)',
                padding: { x: 14, y: 10 },
                titleFont: { size: 13, weight: '600', family: FONT_FAMILY },
                bodyFont: { size: 12, family: FONT_FAMILY },
                titleColor: '#ffffff',
                bodyColor: 'rgba(255, 255, 255, 0.8)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                cornerRadius: 10,
                displayColors: true,
                boxPadding: 4,
                callbacks: {
                    label: function (context) {
                        const value = context.parsed.y;
                        if (value === null) return null;
                        return ` ${context.dataset.label}: ${value.toFixed(unit === 'kWh' ? 2 : 0)} ${unit}`;
                    },
                },
            },
        },
        scales: {
            x: {
                grid: { color: 'rgba(0, 0, 0, 0.04)', drawBorder: false },
                border: { display: false },
                ticks: {
                    color: '#737373',
                    font: { size: 11, family: FONT_FAMILY },
                    maxRotation: 45,
                    minRotation: 45,
                    autoSkip: true,
                    maxTicksLimit: 8,
                    padding: 8,
                },
            },
            y: {
                grid: { color: 'rgba(0, 0, 0, 0.04)', drawBorder: false },
                border: { display: false },
                beginAtZero: true,
                ticks: {
                    color: '#737373',
                    font: { size: 11, family: FONT_FAMILY },
                    padding: 12,
                    callback: (value) => value.toFixed(1) + ' ' + unit,
                },
            },
        },
    }), [unit]);

    const legendItems = [
        { color: CHART_COLORS.actual, label: 'Actual' },
        { color: forecastColor, label: 'Forecast', dashed: isDashed },
    ];

    if (hasRiskData) {
        legendItems.push({ color: CHART_COLORS.atRisk, label: 'At Risk' });
    }

    return (
        <Card className="h-full">
            <CardBody>
                <SectionHeader
                    icon={icon}
                    title={title}
                    subtitle={subtitle}
                    action={extraAction}
                />

                {hasRiskData && (
                    <div className="flex items-center gap-2 mb-4 p-3 bg-red-50 border border-red-100 rounded-xl">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse-soft" />
                        <span className="text-body-sm font-medium text-red-700">
                            Forecast exceeds budget threshold
                        </span>
                    </div>
                )}

                <div style={{ height: `${height}px` }}>
                    <Line data={chartData} options={options} />
                </div>

                <ChartLegend items={legendItems} />
            </CardBody>
        </Card>
    );
}

export default EnergyLineChart;
