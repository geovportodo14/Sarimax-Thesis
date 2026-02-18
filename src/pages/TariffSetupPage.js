import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody, Button, Input } from '../components/ui';
import { useDashboard } from '../context/DashboardContext';

export default function TariffSetupPage() {
    const navigate = useNavigate();
    const { setTariff } = useDashboard();
    const [rate, setRate] = useState(13.47);

    const handleContinue = () => {
        setTariff(Number(rate));
        navigate('/setup/device');
    };

    return (
        <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
            <Card className="max-w-md w-full">
                <CardBody>
                    <h1 className="text-heading-lg text-surface-900 mb-2">Electricity Rate</h1>
                    <p className="text-body-md text-surface-500 mb-6">
                        Enter your current electricity rate to calculate costs accurately.
                    </p>

                    <Input
                        label="Rate per kWh (PHP)"
                        type="number"
                        value={rate}
                        onChange={(e) => setRate(e.target.value)}
                        className="mb-6"
                        prefix="₱"
                    />

                    <Button onClick={handleContinue} className="w-full">
                        Save & Continue
                    </Button>
                </CardBody>
            </Card>
        </div>
    );
}
