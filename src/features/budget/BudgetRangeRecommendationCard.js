import React from 'react';
import { Card, CardBody } from '../../components/ui';

export default function BudgetRangeRecommendationCard({ recommendedMin, recommendedMax }) {
    return (
        <Card className="bg-primary-50 border-primary-200 mb-6">
            <CardBody>
                <div className="flex items-start gap-4">
                    <div className="p-2 bg-white rounded-full text-primary-600 shadow-sm">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-primary-900 mb-1">Recommended Budget</h3>
                        <p className="text-sm text-primary-700 mb-3">
                            Based on your last 30 days of usage, we recommend setting your daily budget between:
                        </p>
                        <div className="flex items-center gap-3">
                            <span className="text-2xl font-bold text-primary-900">₱{recommendedMin.toFixed(2)}</span>
                            <span className="text-primary-400">to</span>
                            <span className="text-2xl font-bold text-primary-900">₱{recommendedMax.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            </CardBody>
        </Card>
    );
}
