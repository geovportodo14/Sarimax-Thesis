import React from 'react';
import { Card, CardBody, Button } from '../../components/ui';
import { Lock } from 'lucide-react';

export default function LockedBudgetCard({ daysLeft }) {
    return (
        <Card className="border-dashed border-2 border-surface-200 bg-surface-50/50">
            <CardBody className="flex flex-col items-center justify-center py-12 text-center">
                <div className="w-12 h-12 bg-surface-100 rounded-full flex items-center justify-center text-surface-400 mb-4">
                    <Lock size={24} />
                </div>
                <h3 className="text-lg font-bold text-surface-900 mb-1">Budget Locked</h3>
                <p className="text-sm text-surface-500 max-w-xs mb-6">
                    We need {daysLeft} more days of usage data to calculate a realistic budget range for you.
                </p>
                <Button variant="outline" size="sm" disabled>
                    Available in {daysLeft} days
                </Button>
            </CardBody>
        </Card>
    );
}
