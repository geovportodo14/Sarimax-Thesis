import React from 'react';
import HowItWorksFlow from '../features/onboarding/HowItWorksFlow';
import { Card } from '../components/ui';

export default function HowItWorksPage() {
    return (
        <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
            <Card className="max-w-2xl w-full p-8 shadow-2xl border-surface-200">
                <HowItWorksFlow />
            </Card>
        </div>
    );
}
