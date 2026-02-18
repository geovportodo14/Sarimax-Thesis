import React from 'react';
import { Card, CardBody } from './ui';

export default function PreviousForecastChart({ previousValue, forecastValue }) {
    const diff = forecastValue - previousValue;
    const Percentage = previousValue > 0 ? (diff / previousValue) * 100 : 0;
    const isIncrease = diff > 0;

    return (
        <Card className="h-full">
            <CardBody>
                <h3 className="text-heading-sm text-surface-900 mb-4">Trend Analysis</h3>

                <div className="space-y-6">
                    <div>
                        <p className="text-body-sm text-surface-500 mb-1">Previous Period Total</p>
                        <p className="text-2xl font-bold text-surface-900">{previousValue.toFixed(2)} kWh</p>
                    </div>

                    <div className="relative pt-6 pb-2">
                        <div className="flex justify-between text-caption text-surface-500 mb-1">
                            <span>Previous</span>
                            <span>Forecast</span>
                        </div>
                        <div className="h-2 bg-surface-100 rounded-full overflow-hidden flex">
                            <div className="bg-surface-400 h-full" style={{ width: '50%' }}></div>
                            <div className={`h-full ${isIncrease ? 'bg-red-500' : 'bg-green-500'}`} style={{ width: '50%' }}></div>
                        </div>
                        <div className="text-center mt-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${isIncrease ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                                {isIncrease ? '+' : ''}{Percentage.toFixed(1)}% {isIncrease ? 'Increase' : 'Decrease'}
                            </span>
                        </div>
                    </div>

                    <div>
                        <p className="text-body-sm text-surface-500 mb-1">Forecasted Total</p>
                        <p className="text-2xl font-bold text-surface-900">{forecastValue.toFixed(2)} kWh</p>
                    </div>
                </div>
            </CardBody>
        </Card>
    );
}
