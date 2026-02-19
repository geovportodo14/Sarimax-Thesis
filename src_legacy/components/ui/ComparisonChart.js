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
import { Card, CardBody, SectionHeader } from './index';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const CHART_COLORS = {
    actual: '#0EA5E9',      // Sky - Actual/Previous
    forecast: '#F59E0B',    // Amber - Forecast
    atRisk: '#EF4444',      // Red
};

const FONT_FAMILY = "'IBM Plex Sans', sans-serif";

export function ComparisonChart({
    previousKwh = 0,
    previousCost = 0,
    forecastKwh = 0,
    forecastCost = 0,
    budgetThreshold = null
}) {
    const isForecastAtRisk = budgetThreshold && forecastKwh > budgetThreshold;

    const chartData = useMemo(() => ({
        labels: ['Energy (kWh)', 'Cost (₱/10)'], // Scaled cost for visibility
        datasets: [
            {
                label: 'Previous 24h',
                data: [previousKwh, previousCost / 10],
                backgroundColor: CHART_COLORS.actual,
                borderRadius: 8,
            },
            {
                label: 'Next 24h',
                data: [forecastKwh, forecastCost / 10],
                backgroundColor: isForecastAtRisk ? CHART_COLORS.atRisk : CHART_COLORS.forecast,
                borderRadius: 8,
            },
        ],
    }), [previousKwh, previousCost, forecastKwh, forecastCost, isForecastAtRisk]);

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(23, 23, 23, 0.95)',
                padding: { x: 12, y: 8 },
                titleFont: { size: 12, weight: '600', family: FONT_FAMILY },
                bodyFont: { size: 11, family: FONT_FAMILY },
                callbacks: {
                    label: (context) => {
                        const label = context.dataset.label;
                        const value = context.raw;
                        if (context.label === 'Cost (₱/10)') {
                            return ` ${label}: ₱${(value * 10).toFixed(2)}`;
                        }
                        return ` ${label}: ${value.toFixed(2)} kWh`;
                    }
                }
            }
        },
        scales: {
            x: { grid: { display: false }, border: { display: false } },
            y: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.04)' }, border: { display: false } }
        }
    };

    const energyChange = previousKwh > 0 ? ((forecastKwh - previousKwh) / previousKwh * 100) : 0;
    const costChange = previousCost > 0 ? ((forecastCost - previousCost) / previousCost * 100) : 0;

    return (
        <Card className="mb-6">
            <CardBody>
                <div className="flex items-center justify-between mb-4">
                    <SectionHeader
                        title="Period Comparison"
                        subtitle="Previous vs forecasted usage"
                        className="mb-0"
                    />
                    <div className="text-right">
                        <div className="text-body-sm font-medium">
                            Energy:
                            <span className={`ml-1 ${energyChange > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                                {energyChange > 0 ? '+' : ''}{energyChange.toFixed(1)}%
                            </span>
                        </div>
                        <div className="text-body-sm font-medium">
                            Cost:
                            <span className={`ml-1 ${costChange > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                                {costChange > 0 ? '+' : ''}{costChange.toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>

                <div className="h-[250px]">
                    <Bar data={chartData} options={options} />
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-surface-50 rounded-xl p-3 border border-surface-100">
                        <div className="text-surface-500 mb-1">Previous Total</div>
                        <div className="font-bold text-surface-900">{previousKwh.toFixed(2)} kWh</div>
                        <div className="text-primary-600 font-medium">₱{previousCost.toFixed(2)}</div>
                    </div>
                    <div className={`rounded-xl p-3 border ${isForecastAtRisk ? 'bg-red-50 border-red-100' : 'bg-primary-50 border-primary-100'}`}>
                        <div className="text-surface-500 mb-1">Next Forecast</div>
                        <div className="font-bold text-surface-900">{forecastKwh.toFixed(2)} kWh</div>
                        <div className={`${isForecastAtRisk ? 'text-red-600' : 'text-primary-600'} font-medium`}>₱{forecastCost.toFixed(2)}</div>
                    </div>
                </div>
            </CardBody>
        </Card>
    );
}

export default ComparisonChart;
