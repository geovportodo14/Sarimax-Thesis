import React from 'react';
import { Card, CardBody } from '../../components/ui';

export default function LearningModeBanner({ daysCollected, daysRequired = 30 }) {
    const daysLeft = Math.max(0, daysRequired - daysCollected);
    const progress = Math.min(100, (daysCollected / daysRequired) * 100);

    return (
        <div className="bg-amber-50 border-b border-amber-200 px-4 py-3 mb-6">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-amber-100 rounded-full text-amber-600">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div>
                        <p className="text-sm font-bold text-amber-900">Learning Mode Active</p>
                        <p className="text-xs text-amber-700">
                            We need {daysLeft} more days of data to unlock smart budget recommendations.
                        </p>
                    </div>
                </div>

                <div className="hidden sm:block w-32">
                    <div className="h-2 bg-amber-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-amber-500 transition-all duration-500"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <p className="text-xs text-right text-amber-700 mt-1">{daysCollected}/{daysRequired} days</p>
                </div>
            </div>
        </div>
    );
}
