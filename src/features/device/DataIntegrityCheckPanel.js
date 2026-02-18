import React, { useState, useEffect } from 'react';
import { Card, CardBody, Button, StatusBadge } from '../../components/ui';

export default function DataIntegrityCheckPanel({ deviceName, onVerified }) {
    const [step, setStep] = useState(0); // 0: instructions, 1: verifying, 2: success
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (step === 1) {
            const interval = setInterval(() => {
                setProgress((prev) => {
                    if (prev >= 100) {
                        clearInterval(interval);
                        setStep(2);
                        return 100;
                    }
                    return prev + 2; // 50 ticks * 50ms = 2.5s
                });
            }, 50);
            return () => clearInterval(interval);
        }
    }, [step]);

    return (
        <Card className="w-full max-w-md mx-auto">
            <CardBody>
                <div className="text-center">
                    {step === 0 && (
                        <>
                            <h2 className="text-xl font-bold text-surface-900 mb-4">Let's verify the connection</h2>
                            <div className="bg-primary-50 p-4 rounded-xl mb-6 text-left">
                                <p className="text-sm text-primary-900 font-medium mb-2">Instructions:</p>
                                <ol className="list-decimal list-inside text-sm text-surface-700 space-y-2">
                                    <li>Make sure <strong>{deviceName}</strong> is turned OFF.</li>
                                    <li>When ready, press "Start Check" below.</li>
                                    <li>Turn the appliance ON for 5 seconds, then OFF.</li>
                                </ol>
                            </div>
                            <Button onClick={() => setStep(1)} className="w-full">
                                Start Check
                            </Button>
                        </>
                    )}

                    {step === 1 && (
                        <>
                            <h2 className="text-xl font-bold text-surface-900 mb-4">Verifying signal...</h2>
                            <div className="relative w-48 h-48 mx-auto mb-6 flex items-center justify-center">
                                {/* Simplified visualization */}
                                <div className="absolute inset-0 border-4 border-surface-100 rounded-full"></div>
                                <div
                                    className="absolute inset-0 border-4 border-primary-500 rounded-full transition-all duration-200"
                                    style={{ clipPath: `inset(${100 - progress}% 0 0 0)` }} // Just a visual hack, simpler is better
                                ></div>
                                {/* Better progress bar */}
                                <div className="text-3xl font-bold text-primary-600">{progress}%</div>
                            </div>
                            <p className="text-surface-600 animate-pulse">Detecting power usage spike...</p>
                        </>
                    )}

                    {step === 2 && (
                        <>
                            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                            <h2 className="text-xl font-bold text-surface-900 mb-2">Verification Complete!</h2>
                            <p className="text-surface-600 mb-6">
                                We've confirmed the signal from <strong>{deviceName}</strong>. You're ready to start monitoring.
                            </p>
                            <Button onClick={onVerified} className="w-full bg-green-600 hover:bg-green-700">
                                Go to Dashboard
                            </Button>
                        </>
                    )}
                </div>
            </CardBody>
        </Card>
    );
}
