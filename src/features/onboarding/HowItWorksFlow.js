import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Button, Card } from '../../components/ui';
import { ChevronRight, Check } from 'lucide-react';

const steps = [
    {
        id: 1,
        title: "Track & Predict",
        description: "See your electricity usage in real-time and predict your next bill before it arrives.",
        image: "/assets/onboarding-1.svg", // Placeholder
        icon: (
            <svg className="w-12 h-12 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
        )
    },
    {
        id: 2,
        title: "Simulate Scenarios",
        description: "What if you run the AC for 2 more hours? See the cost impact instantly.",
        image: "/assets/onboarding-2.svg",
        icon: (
            <svg className="w-12 h-12 text-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
        )
    },
    {
        id: 3,
        title: "Optimize Budget",
        description: "Set a smart budget range and get alerts when you're drifting off track.",
        image: "/assets/onboarding-3.svg",
        icon: (
            <svg className="w-12 h-12 text-tertiary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        )
    }
];

export default function HowItWorksFlow() {
    const [currentStep, setCurrentStep] = useState(0);
    const navigate = useNavigate();

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            navigate('/setup/tariff');
        }
    };

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-md mx-auto p-4">
            <div className="w-full relative h-96 mb-8">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="absolute inset-0 flex flex-col items-center text-center"
                    >
                        <div className="w-32 h-32 bg-surface-100 rounded-full flex items-center justify-center mb-6 shadow-card">
                            {steps[currentStep].icon}
                        </div>
                        <h2 className="text-display-sm font-bold text-surface-900 mb-4">
                            {steps[currentStep].title}
                        </h2>
                        <p className="text-body-lg text-surface-600">
                            {steps[currentStep].description}
                        </p>
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Indicators */}
            <div className="flex gap-2 mb-8">
                {steps.map((_, index) => (
                    <div
                        key={index}
                        className={`h-2 rounded-full transition-all duration-300 ${index === currentStep ? 'w-8 bg-primary-600' : 'w-2 bg-surface-200'
                            }`}
                    />
                ))}
            </div>

            <Button onClick={handleNext} className="w-full h-12 text-lg group">
                {currentStep === steps.length - 1 ? 'Get Started' : 'Next'}
                {currentStep === steps.length - 1 ? (
                    <Check className="ml-2 w-5 h-5" />
                ) : (
                    <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                )}
            </Button>
        </div>
    );
}
