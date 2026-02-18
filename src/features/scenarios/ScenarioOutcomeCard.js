import React from 'react';
import { Card, CardBody, StatusBadge } from '../../components/ui';

export default function ScenarioOutcomeCard({ baselineCost, scenarioCost }) {
    const difference = scenarioCost - baselineCost;
    const percentage = baselineCost > 0 ? (difference / baselineCost) * 100 : 0;
    const isSaving = difference < 0;

    return (
        <Card className="bg-white border-surface-200 shadow-sm h-full">
            <CardBody>
                <h3 className="text-sm font-bold text-surface-500 uppercase tracking-wider mb-2">Projected Impact</h3>

                <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-3xl font-bold text-surface-900">₱{Math.abs(difference).toFixed(2)}</span>
                    <StatusBadge variant={isSaving ? 'success' : 'danger'}>
                        {isSaving ? 'Savings' : 'Increase'}
                    </StatusBadge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm border-t border-surface-100 pt-4">
                    <div>
                        <p className="text-surface-500">Baseline Cost</p>
                        <p className="font-semibold text-surface-900">₱{baselineCost.toFixed(2)}</p>
                    </div>
                    <div>
                        <p className="text-surface-500">Scenario Cost</p>
                        <p className={`font-semibold ${isSaving ? 'text-green-600' : 'text-red-600'}`}>
                            ₱{scenarioCost.toFixed(2)}
                        </p>
                    </div>
                </div>
            </CardBody>
        </Card>
    );
}
