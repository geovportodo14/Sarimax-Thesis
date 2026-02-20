import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, X, Play, AlertTriangle } from 'lucide-react';
import { useDashboard } from '../../context/DashboardContext';

const OnboardingModal = () => {
    const { showSetupWizard, handleCompleteSetup } = useDashboard();
    const [step, setStep] = useState(0);

    // If not showing, render nothing
    if (!showSetupWizard) return null;

    const steps = [
        {
            title: "Step 1: Power & Reset",
            text: "Plug in your smart device. Hold the power button for 5 seconds until the LED indicator flashes rapidly (EZ Mode).",
            image: <img src="/blink.png" alt="Blinking smart plug" className="w-full h-full object-contain drop-shadow-sm rounded-md" />,
        },
        {
            title: "Step 2: Smart Life App Pairing",
            text: "Open the Smart Life app, add your device, and connect it via your 2.4GHz Wi-Fi.",
            image: <img src="/adddevice.png" alt="Add device in Smart Life" className="w-full h-full object-contain drop-shadow-sm rounded-md" />,
        },
        {
            title: "Step 3: Establish Identity",
            text: "Rename your device (e.g., 'Aircon'). This is crucial for the system to identify the correct data stream.",
            warning: "⚠️ Data Integrity Rule: Only the assigned appliance should use this plug to ensure accurate forecasting.",
            image: <img src="/rename.png" alt="Rename appliance" className="w-full h-full object-contain drop-shadow-sm rounded-md" />,
        },
        {
            title: "Step 4: Tuya Cloud API Authorization",
            text: "Link your app account to the Tuya IoT Platform. Your renamed devices will appear in the device list, authorizing Sarimax to pull the data.",
            image: <img src="/devicelist.png" alt="Tuya Cloud Device List" className="w-full h-full object-contain drop-shadow-sm rounded-md" />,
        },
        {
            title: "Step 5: Dashboard Activation",
            text: "Setup Complete! Sarimax is now connected to your appliance. Click 'Enter Dashboard' to view your real-time energy forecast.",
            image: <img src="/appliancedashboard.png" alt="Sarimax Dashboard" className="w-full h-full object-cover drop-shadow-sm rounded-md" />,
        }
    ];

    const currentStep = steps[step];

    const handleNext = () => {
        if (step < steps.length - 1) {
            setStep(step + 1);
        } else {
            handleCompleteSetup();
            setStep(0); // Reset for next time if re-triggered
        }
    };

    const handleBack = () => {
        if (step > 0) {
            setStep(step - 1);
        }
    };

    const handleClose = () => {
        handleCompleteSetup();
        setStep(0);
    };

    return (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/60 backdrop-blur-xl animate-in fade-in duration-300 p-4 sm:p-8">
            {/* Modal Container: Full mobile, 2-column desktop */}
            <div className="bg-white w-full max-w-5xl max-h-[85vh] overflow-y-auto rounded-3xl shadow-2xl flex flex-col md:flex-row md:h-[600px] transition-all duration-300 relative animate-in zoom-in-95">

                {/* Close Button (Absolute Top-Right of Modal) */}
                <button
                    onClick={handleClose}
                    className="absolute top-4 right-4 p-2 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-full transition-colors z-[100] bg-white/50 md:bg-transparent"
                    aria-label="Close setup wizard"
                >
                    <X size={20} />
                </button>

                {/* Left Column: Text & Controls */}
                <div className="w-full md:w-1/2 h-1/2 md:h-full flex flex-col justify-between p-6 md:p-10 bg-white z-10 order-2 md:order-1">
                    <div>
                        <div className="mb-8">
                            <h2 className="text-xl md:text-3xl font-bold text-surface-900 mb-4">{currentStep.title}</h2>
                            <p className="text-surface-600 text-base md:text-lg leading-relaxed">
                                {currentStep.text}
                            </p>
                        </div>

                        {currentStep.warning && (
                            <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg flex items-start gap-3 mt-4">
                                <AlertTriangle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
                                <p className="text-amber-800 text-sm md:text-base font-medium">
                                    {currentStep.warning}
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="mt-8 space-y-6">
                        {/* Progress Dots */}
                        <div className="flex gap-2">
                            {steps.map((_, i) => (
                                <div
                                    key={i}
                                    className={`h-2 rounded-full transition-all duration-300 ${i === step ? 'w-8 bg-primary-600' : 'w-2 bg-surface-200'}`}
                                />
                            ))}
                        </div>

                        {/* Navigation Buttons */}
                        <div className="flex items-center justify-between pt-4 border-t border-surface-100">
                            {step > 0 ? (
                                <button
                                    onClick={handleBack}
                                    className="flex items-center gap-2 px-4 py-2 text-surface-600 font-medium hover:text-surface-900 transition-colors"
                                >
                                    <ChevronLeft size={18} /> Back
                                </button>
                            ) : (
                                <div></div> // Spacer to keep Next button on the right
                            )}

                            <button
                                onClick={handleNext}
                                className="flex items-center gap-2 px-6 lg:px-8 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-md active:scale-95 w-auto"
                            >
                                {step < steps.length - 1 ? (
                                    <>Next <ChevronRight size={18} /></>
                                ) : (
                                    <>Enter Dashboard <Play size={18} fill="currentColor" /></>
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Column: Image Display */}
                <div className="bg-slate-50 w-full h-56 sm:h-64 md:w-1/2 md:h-full flex-shrink-0 flex items-center justify-center border-b md:border-b-0 md:border-l border-slate-100 order-1 md:order-2 overflow-hidden p-4 sm:p-8">
                    {currentStep.image}
                </div>

            </div>
        </div>
    );
};

export default OnboardingModal;
