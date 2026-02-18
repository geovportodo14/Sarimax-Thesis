import React, { useState, useEffect } from 'react';
import { Card, CardBody, Button, StatusBadge } from '../../components/ui';

export default function DevicePairingCard({ onPairComplete }) {
    const [status, setStatus] = useState('idle'); // idle, scanning, found, connecting, success

    const startScanning = () => {
        setStatus('scanning');
        // Simulate finding a device
        setTimeout(() => {
            setStatus('found');
        }, 2000);
    };

    const connectDevice = () => {
        setStatus('connecting');
        // Simulate connection
        setTimeout(() => {
            setStatus('success');
            setTimeout(onPairComplete, 1000);
        }, 1500);
    };

    return (
        <Card className="w-full max-w-md mx-auto overflow-hidden">
            <div className="bg-primary-50 p-6 flex flex-col items-center justify-center text-center">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg mb-4 relative">
                    {status === 'scanning' && (
                        <div className="absolute inset-0 border-4 border-primary-400 rounded-full animate-ping opacity-25"></div>
                    )}
                    <svg className={`w-12 h-12 ${status === 'success' ? 'text-green-500' : 'text-primary-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>

                <h3 className="text-xl font-bold text-surface-900 mb-2">
                    {status === 'idle' && 'Connect Smart Plug'}
                    {status === 'scanning' && 'Searching for devices...'}
                    {status === 'found' && 'Device Found!'}
                    {status === 'connecting' && 'Connecting...'}
                    {status === 'success' && 'Connected Successfully'}
                </h3>

                <p className="text-surface-600 text-sm mb-6">
                    {status === 'idle' && 'Make sure your smart plug is plugged in and the LED is blinking.'}
                    {status === 'scanning' && 'Hold your phone near the device.'}
                    {status === 'found' && 'Found "Smart Plug 01"'}
                    {status === 'connecting' && 'Establishing secure connection...'}
                    {status === 'success' && 'Redirecting to setup...'}
                </p>

                {status === 'idle' && (
                    <Button onClick={startScanning} size="lg" className="w-full">
                        Start Scanning
                    </Button>
                )}

                {status === 'found' && (
                    <Button onClick={connectDevice} size="lg" className="w-full">
                        Connect Device
                    </Button>
                )}
            </div>
        </Card>
    );
}
