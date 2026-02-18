import React from 'react';
import { Card, CardBody, Input } from '../../components/ui';

export default function RangeSlider({ minValue, maxValue, onChangeMin, onChangeMax, minLimit = 0, maxLimit = 1000 }) {
    // Simplistic implementation using two number inputs and a visual bar
    // Ideally this would be a dual-thumb slider

    const rangeWidth = ((maxValue - minValue) / (maxLimit - minLimit)) * 100;
    const rangeLeft = ((minValue - minLimit) / (maxLimit - minLimit)) * 100;

    return (
        <Card className="mb-6">
            <CardBody>
                <h3 className="text-lg font-bold text-surface-900 mb-4">Set Your Target Range</h3>

                {/* Visual Bar */}
                <div className="relative h-4 bg-surface-100 rounded-full mb-8">
                    <div
                        className="absolute top-0 bottom-0 bg-primary-500 rounded-full opacity-20"
                        style={{ left: `${rangeLeft}%`, width: `${rangeWidth}%` }}
                    ></div>
                    {/* Thumbs (visual only) */}
                    <div
                        className="absolute top-1/2 -mt-3 w-6 h-6 bg-white border-2 border-primary-500 rounded-full shadow-md transform -translate-x-1/2 cursor-grab"
                        style={{ left: `${rangeLeft}%` }}
                    ></div>
                    <div
                        className="absolute top-1/2 -mt-3 w-6 h-6 bg-white border-2 border-primary-500 rounded-full shadow-md transform -translate-x-1/2 cursor-grab"
                        style={{ left: `${rangeLeft + rangeWidth}%` }}
                    ></div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-surface-700 mb-2">Minimum (₱)</label>
                        <Input
                            type="number"
                            value={minValue}
                            onChange={(e) => onChangeMin(Number(e.target.value))}
                            min={minLimit}
                            max={maxValue}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-surface-700 mb-2">Maximum (₱)</label>
                        <Input
                            type="number"
                            value={maxValue}
                            onChange={(e) => onChangeMax(Number(e.target.value))}
                            min={minValue}
                            max={maxLimit}
                        />
                    </div>
                </div>
            </CardBody>
        </Card>
    );
}
