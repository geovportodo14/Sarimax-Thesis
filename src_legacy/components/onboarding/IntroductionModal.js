import React, { useState } from 'react';

const IntroductionModal = ({ isOpen, onSkip, onNext }) => {
    const [step, setStep] = useState(0);

    const steps = [
        {
            title: "Welcome to Smart Home Monitoring",
            description: "Smart Home Monitoring is your personal energy intelligence dashboard. We help you understand, predict, and optimize your home's energy consumption using advanced SARIMAX forecasting models.",
            icon: (
                <svg className="w-12 h-12 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            ),
            color: "bg-primary-50",
        },
        {
            title: "What is Energy Forecasting?",
            description: "Forecasting isn't just a guess—it's math. We analyze your past usage patterns and external factors to predict exactly how much energy you'll use in the coming hours and days.",
            icon: (
                <svg className="w-12 h-12 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
            ),
            color: "bg-sky-50",
        },
        {
            title: "Budget Thresholds",
            description: "Set a monthly budget, and we'll tell you if you're on track to exceed it. Our system calculates your 'Risk Status' in real-time.",
            icon: (
                <svg className="w-12 h-12 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            ),
            color: "bg-amber-50",
        },
        {
            title: "Understanding Metrics",
            description: "We translate complex energy data (kWh) into local currency (₱). See which appliances are costing you the most.",
            icon: (
                <svg className="w-12 h-12 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
            ),
            color: "bg-emerald-50",
        },
        {
            title: "Make Smarter Decisions",
            description: "Use Smart Home Monitoring to decide the best time to run heavy appliances or to identify hidden energy drainers.",
            icon: (
                <svg className="w-12 h-12 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            ),
            color: "bg-indigo-50",
        }
    ];

    if (!isOpen) return null;

    const currentStep = steps[step];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-900/60 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                {/* Close Button */}
                <button
                    onClick={onSkip}
                    className="absolute top-4 right-4 p-2 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-full transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>

                {/* Modal Content */}
                <div className="p-8 pb-6">
                    <div className="flex flex-col items-center text-center">
                        {/* Icon Container */}
                        <div className={`w-24 h-24 ${currentStep.color} rounded-2xl flex items-center justify-center mb-6 shadow-sm`}>
                            {currentStep.icon}
                        </div>

                        {/* Title & Description */}
                        <h2 className="text-2xl font-bold text-surface-900 mb-3">{currentStep.title}</h2>
                        <p className="text-surface-600 leading-relaxed mb-8">
                            {currentStep.description}
                        </p>

                        {/* Progress Indicators */}
                        <div className="flex gap-2 mb-8">
                            {steps.map((_, i) => (
                                <div
                                    key={i}
                                    className={`h-1.5 rounded-full transition-all duration-300 ${i === step ? 'w-8 bg-primary-500' : 'w-2 bg-surface-200'
                                        }`}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="p-6 bg-surface-50 border-t border-surface-100 flex items-center justify-between">
                    <button
                        onClick={onSkip}
                        className="px-4 py-2 text-surface-500 font-medium hover:text-surface-700 transition-colors"
                    >
                        Skip Guide
                    </button>

                    <div className="flex gap-3">
                        {step < steps.length - 1 ? (
                            <button
                                onClick={() => setStep(step + 1)}
                                className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-md active:scale-95"
                            >
                                Next <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                            </button>
                        ) : (
                            <button
                                onClick={onNext}
                                className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-md active:scale-95"
                            >
                                Let's Start <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" /></svg>
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntroductionModal;
