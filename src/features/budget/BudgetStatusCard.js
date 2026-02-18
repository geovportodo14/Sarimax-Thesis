import React from 'react';
import { Card, CardBody, StatusBadge } from '../../components/ui';

export default function BudgetStatusCard({ currentCost, minBudget, maxBudget }) {
    let status = 'within_range'; // within_range, approaching_limit, exceeded, below_target
    if (currentCost > maxBudget) status = 'exceeded';
    else if (currentCost > maxBudget * 0.9) status = 'approaching_limit';
    else if (currentCost < minBudget) status = 'below_target';

    const statusConfig = {
        within_range: { label: 'On Track', color: 'success', message: 'You are well within your budget range.' },
        approaching_limit: { label: 'Near Limit', color: 'warning', message: 'You are close to your maximum budget.' },
        exceeded: { label: 'Over Budget', color: 'danger', message: 'You have exceeded your maximum budget.' },
        below_target: { label: 'Below Target', color: 'success', message: 'Great job! You are below your minimum target.' },
    };

    const { label, color, message } = statusConfig[status];
    const percentage = Math.min(100, (currentCost / maxBudget) * 100);

    return (
        <Card>
            <CardBody>
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-surface-900">Current Status</h3>
                    <StatusBadge variant={color}>{label}</StatusBadge>
                </div>

                <div className="mb-2 flex justify-between text-sm text-surface-600">
                    <span>Spent: ₱{currentCost.toFixed(2)}</span>
                    <span>Max: ₱{maxBudget.toFixed(2)}</span>
                </div>

                <div className="h-3 bg-surface-100 rounded-full overflow-hidden mb-4">
                    <div
                        className={`h-full transition-all duration-500 ${status === 'exceeded' ? 'bg-red-500' :
                                status === 'approaching_limit' ? 'bg-amber-500' : 'bg-green-500'
                            }`}
                        style={{ width: `${percentage}%` }}
                    ></div>
                </div>

                <p className="text-sm text-surface-600">{message}</p>
            </CardBody>
        </Card>
    );
}
