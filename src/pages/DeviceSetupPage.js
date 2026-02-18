import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DevicePairingCard from '../features/device/DevicePairingCard';
import DeviceNamingForm from '../features/device/DeviceNamingForm';
import DataIntegrityCheckPanel from '../features/device/DataIntegrityCheckPanel';
import { useDashboard } from '../context/DashboardContext';

export default function DeviceSetupPage() {
    const navigate = useNavigate();
    const { setOnboardingComplete } = useDashboard();
    const [step, setStep] = useState('pairing'); // pairing, naming, verifying
    const [deviceData, setDeviceData] = useState(null);

    const handlePairComplete = () => {
        setStep('naming');
    };

    const handleNamingComplete = (data) => {
        setDeviceData(data);
        setStep('verifying');
    };

    const handleVerified = () => {
        // Save device to context/storage (simulated)
        console.log('Device Setup Complete:', deviceData);

        // Mark onboarding as complete in context
        if (setOnboardingComplete) {
            setOnboardingComplete(true);
        }

        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
            <div className="w-full max-w-lg">
                {/* Progress Indicator */}
                <div className="flex justify-center mb-8 gap-2">
                    <div className={`h-1.5 w-8 rounded-full ${step === 'pairing' ? 'bg-primary-500' : 'bg-primary-200'}`}></div>
                    <div className={`h-1.5 w-8 rounded-full ${step === 'naming' ? 'bg-primary-500' : 'bg-primary-200'}`}></div>
                    <div className={`h-1.5 w-8 rounded-full ${step === 'verifying' ? 'bg-primary-500' : 'bg-primary-200'}`}></div>
                </div>

                {step === 'pairing' && (
                    <DevicePairingCard onPairComplete={handlePairComplete} />
                )}

                {step === 'naming' && (
                    <DeviceNamingForm onComplete={handleNamingComplete} />
                )}

                {step === 'verifying' && (
                    <DataIntegrityCheckPanel
                        deviceName={deviceData?.name || 'Device'}
                        onVerified={handleVerified}
                    />
                )}
            </div>
        </div>
    );
}
