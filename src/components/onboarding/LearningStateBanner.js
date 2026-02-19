import React from 'react';
import { Card, CardBody } from '../ui';

export default function LearningStateBanner({ progress = 30, daysRemaining = 3 }) {
    return (
        <Card className="mb-6 border-l-4 border-l-amber-400 bg-amber-50">
            <CardBody className="p-5">
                <div className="flex flex-col sm:flex-row gap-5 items-start sm:items-center">

                    {/* Icon */}
                    <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center text-amber-600">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="flex-grow">
                        <h3 className="text-lg font-semibold text-amber-900 mb-1">
                            System is Learning Your Home's Profile
                        </h3>
                        <p className="text-amber-700/80 text-sm mb-3">
                            We need a bit more data to accurately recommend a budget and forecast your costs.
                            Please use your appliances as normal.
                        </p>

                        {/* Progress Bar */}
                        <div className="w-full max-w-md">
                            <div className="flex justify-betweentext-xs font-medium text-amber-800 mb-1">
                                <span>Data Collection</span>
                                <span>{progress}%</span>
                            </div>
                            <div className="w-full bg-amber-200 rounded-full h-2.5">
                                <div
                                    className="bg-amber-500 h-2.5 rounded-full transition-all duration-1000"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-amber-600 mt-1">
                                Estimated completion: {daysRemaining} days
                            </p>
                        </div>
                    </div>

                    {/* Locked Badge */}
                    <div className="hidden sm:block flex-shrink-0">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-white/60 text-amber-700 border border-amber-200/50">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            Budget Locked
                        </span>
                    </div>

                </div>
            </CardBody>
        </Card>
    );
}
