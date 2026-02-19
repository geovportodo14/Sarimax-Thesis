import React from 'react';
import { Card, CardBody } from './ui';
import EnergyLineChart from './ui/EnergyLineChart';
import { ApplianceIcons } from './ui/icons';

export default function ApplianceAnalytics({ calculations, chartData, tariff, labels }) {
    const appliances = [
        { key: 'fan', name: 'Electric Fan', icon: ApplianceIcons.ElectricFan, color: '#3B82F6' },
        { key: 'ac', name: 'Air Conditioner', icon: ApplianceIcons.AirConditioner, color: '#8B5CF6' },
        { key: 'ref', name: 'Refrigerator', icon: ApplianceIcons.Refrigerator, color: '#10B981' },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {appliances.map((app) => {
                const data = calculations.applianceData[app.name];
                const forecastPoints = data?.data || [];

                // Align data with labels
                // forecastPoints corresponds to nextLabels
                // We might want to show some history if available, but App.js only passes nextForecasts in applianceData
                // chartData.nextApplianceForecasts has the data

                // Let's construct the full series
                // actualData: likely 0 or mock history for appliances?
                // For simplicity, let's just show the forecast for now as per App.js data structure

                const fullForecast = forecastPoints;
                const fullActual = Array(labels.prevPoints).fill(0).concat(Array(labels.nextPoints).fill(null)); // Mock history for visual balance

                // If we want to show history, we need appliance usage history which might complicate things
                // For now, let's just show the forecast

                return (
                    <Card key={app.key} className="overflow-hidden">
                        <CardBody className="p-0">
                            <div className="h-64 p-4">
                                <EnergyLineChart
                                    title={app.name}
                                    subtitle="Actual vs Forecast"
                                    startLine={1}
                                    variant="default"
                                    labels={[...labels.prevLabels, ...labels.nextLabels]}
                                    actualData={fullActual}
                                    forecastData={fullForecast}
                                    forecastColor={app.color}
                                    isDashed={true}
                                    unit="kWh"
                                    responsiveHeader={true}
                                    height={240}
                                />
                            </div>
                        </CardBody>
                    </Card>
                );
            })}
        </div >
    );
}
