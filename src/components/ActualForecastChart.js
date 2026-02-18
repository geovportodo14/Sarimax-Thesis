import React from 'react';
import { Line } from 'react-chartjs-2';
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

export default function ActualForecastChart({
    labels,
    actualData,
    forecastData,
    allTime,
    onAllTimeChange,
    selectedFilter,
    onFilterChange,
    applianceFilters = [],
    customDatasets = null
}) {

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                position: 'top',
                align: 'end',
                labels: {
                    usePointStyle: true,
                    boxWidth: 8,
                    color: '#64748b', // surafce-500
                    font: { family: 'Inter, sans-serif', size: 12 }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                titleColor: '#0f172a',
                bodyColor: '#334155',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 10,
                boxPadding: 4,
                usePointStyle: true,
                callbacks: {
                    label: function (context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(2) + ' kWh';
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: '#94a3b8', font: { size: 11 } }
            },
            y: {
                border: { display: false },
                grid: { color: '#f1f5f9' },
                ticks: { color: '#94a3b8', font: { size: 11 } }
            }
        }
    };

    const defaultDatasets = [
        {
            label: 'Actual Usage',
            data: actualData,
            borderColor: '#3b82f6', // primary-500
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointRadius: 0,
            pointHoverRadius: 4
        },
        {
            label: 'Forecast',
            data: forecastData,
            borderColor: '#8b5cf6', // Indigo-500 (distinct from actual)
            borderDash: [5, 5],
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 4
        }
    ];

    const data = {
        labels,
        datasets: customDatasets || defaultDatasets
    };

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-surface-200">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
                <div>
                    <h3 className="text-heading-sm text-surface-900">Energy Consumption</h3>
                    <p className="text-body-sm text-surface-500 hidden sm:block">Actual vs Forecasted usage over time</p>
                </div>

                <div className="flex items-center gap-2">
                    {applianceFilters.length > 0 && (
                        <select
                            value={selectedFilter}
                            onChange={(e) => onFilterChange(e.target.value)}
                            className="text-body-sm border-surface-200 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                        >
                            {applianceFilters.map(filter => (
                                <option key={filter} value={filter}>{filter}</option>
                            ))}
                        </select>
                    )}
                    <div className="flex bg-surface-100 p-1 rounded-lg">
                        <button
                            onClick={() => onAllTimeChange(false)}
                            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${!allTime ? 'bg-white text-surface-900 shadow-sm' : 'text-surface-500 hover:text-surface-700'}`}
                        >
                            Recent
                        </button>
                        <button
                            onClick={() => onAllTimeChange(true)}
                            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${allTime ? 'bg-white text-surface-900 shadow-sm' : 'text-surface-500 hover:text-surface-700'}`}
                        >
                            All Time
                        </button>
                    </div>
                </div>
            </div>

            <div className="h-[300px] w-full">
                <Line options={options} data={data} />
            </div>
        </div>
    );
}
