import React from 'react';
import { Card, CardBody } from './ui/index';

function ColorLegend({ className = '' }) {
    const legendItems = [
        {
            color: 'bg-emerald-500',
            label: 'Optimal / Efficient',
            description: 'Usage is well within budget (< 80%)',
        },
        {
            color: 'bg-amber-500',
            label: 'Warning / Caution',
            description: 'Usage is approaching budget limits (80% - 100%)',
        },
        {
            color: 'bg-red-500',
            label: 'Critical / Action Needed',
            description: 'Usage has exceeded the set budget (> 100%)',
        },
        {
            color: 'bg-primary-500',
            label: 'Forecast / Projection',
            description: 'Predicted usage based on historical data',
        },
    ];

    return (
        <Card className={`mt-6 ${className}`}>
            <CardBody>
                <h4 className="text-body-sm font-semibold text-surface-600 mb-4 uppercase tracking-wide">
                    Dashboard Color Guide
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {legendItems.map((item, index) => (
                        <div key={index} className="flex items-start gap-3">
                            <span
                                className={`w-3 h-3 mt-1.5 rounded-full flex-shrink-0 ${item.color}`}
                                aria-hidden="true"
                            />
                            <div>
                                <p className="text-body-sm font-medium text-surface-900">
                                    {item.label}
                                </p>
                                <p className="text-caption text-surface-500 leading-tight mt-0.5">
                                    {item.description}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </CardBody>
        </Card>
    );
}

export default ColorLegend;
