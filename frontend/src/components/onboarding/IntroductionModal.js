import React, { useState } from 'react';
import {
    Zap,
    Target,
    BarChart3,
    TrendingUp,
    Lightbulb,
    ChevronRight,
    X,
    Play
} from 'lucide-react';

const IntroductionModal = ({ isOpen, onSkip, onNext }) => {
    const [step, setStep] = useState(0);

    const steps = [
        {
            title: "Welcome to Smart Home Monitoring",
            description: "Smart Home Monitoring is your personal energy intelligence dashboard. We help you understand, predict, and optimize your home's energy consumption using advanced SARIMAX forecasting models.",
            icon: <Zap className="w-12 h-12 text-primary-500" />,
            color: "bg-primary-50",
        },
        {
            title: "What is Energy Forecasting?",
            description: "Forecasting isn't just a guess—it's math. We analyze your past usage patterns and external factors to predict exactly how much energy you'll use in the coming hours and days. This helps you avoid surprises on your next bill.",
            icon: <TrendingUp className="w-12 h-12 text-sky-500" />,
            color: "bg-sky-50",
        },
        {
            title: "Budget Thresholds",
            description: "Set a monthly budget, and we'll tell you if you're on track to exceed it. Our system calculates your 'Risk Status' in real-time, helping you decide when to dial back usage to save money.",
            icon: <Target className="w-12 h-12 text-amber-500" />,
            color: "bg-amber-50",
        },
        {
            title: "Understanding Metrics",
            description: "We translate complex energy data (kWh) into local currency (₱). You can see which specific appliances—like your Air Conditioner or Fridge—are costing you the most right now and in the future.",
            icon: <BarChart3 className="w-12 h-12 text-emerald-500" />,
            color: "bg-emerald-50",
        },
        {
            title: "Make Smarter Decisions",
            description: "Use Smart Home Monitoring to decide the best time to run heavy appliances or to identify hidden energy drainers. Ready to take control of your energy bill?",
            icon: <Lightbulb className="w-12 h-12 text-indigo-500" />,
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
                    <X size={20} />
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
                                Next <ChevronRight size={18} />
                            </button>
                        ) : (
                            <button
                                onClick={onNext}
                                className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-md active:scale-95"
                            >
                                Let's Start <Play size={18} fill="currentColor" />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntroductionModal;
