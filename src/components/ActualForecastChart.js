import React, { useMemo } from 'react';
import EnergyLineChart from './ui/EnergyLineChart';

function ActualForecastChart({
    labels,
    actualData,
    forecastData,
    allTime,
    onAllTimeChange,
    selectedFilter,
    onFilterChange,
    applianceFilters,
    customDatasets
}) {

    return (
        <EnergyLineChart
            title="Aggregated Building Energy"
            subtitle="Actual vs Forecast"
            icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            }
            labels={labels}
            actualData={actualData}
            forecastData={forecastData}
            unit="kWh"
        />
    );
}

export default ActualForecastChart;
