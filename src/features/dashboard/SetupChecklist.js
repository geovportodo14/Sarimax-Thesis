import React from 'react';
import { Card, CardBody } from '../../components/ui';
import { Check, Circle } from 'lucide-react';

export default function SetupChecklist({ completedSteps = [] }) {
    const allSteps = [
        { id: 'tariff', label: 'Set Electricity Rate' },
        { id: 'device', label: 'Connect First Device' },
        { id: 'notifications', label: 'Enable Notifications' },
    ];

    return (
        <Card>
            <CardBody>
                <h3 className="text-lg font-bold text-surface-900 mb-4">Setup Checklist</h3>
                <div className="space-y-3">
                    {allSteps.map(step => {
                        const isCompleted = completedSteps.includes(step.id);
                        return (
                            <div key={step.id} className="flex items-center gap-3">
                                {isCompleted ? (
                                    <div className="w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                                        <Check size={14} strokeWidth={3} />
                                    </div>
                                ) : (
                                    <div className="w-6 h-6 rounded-full border-2 border-surface-200 text-surface-300 flex items-center justify-center">
                                        <div className="w-2 h-2 rounded-full bg-current opacity-0"></div>
                                    </div>
                                )}
                                <span className={`text-sm ${isCompleted ? 'text-surface-900 font-medium' : 'text-surface-500'}`}>
                                    {step.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </CardBody>
        </Card>
    );
}
