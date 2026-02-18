import React, { useState } from 'react';
import { Card, CardBody, Button, Input, Select } from '../../components/ui';

const applianceTypes = [
    { value: 'air_conditioner', label: 'Air Conditioner' },
    { value: 'refrigerator', label: 'Refrigerator' },
    { value: 'washing_machine', label: 'Washing Machine' },
    { value: 'electric_fan', label: 'Electric Fan' },
    { value: 'water_heater', label: 'Water Heater' },
    { value: 'other', label: 'Other Appliance' },
];

export default function DeviceNamingForm({ onComplete }) {
    const [name, setName] = useState('');
    const [type, setType] = useState(applianceTypes[0].value);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (name) {
            onComplete({ name, type });
        }
    };

    return (
        <Card className="w-full max-w-md mx-auto">
            <CardBody>
                <h2 className="text-xl font-bold text-surface-900 mb-2">Name Your Device</h2>
                <p className="text-surface-600 mb-6 text-sm">
                    Give your device a recognizable name and select what appliance is connected to it.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <Input
                        label="Device Name"
                        placeholder="e.g. Master Bedroom AC"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />

                    <div className="space-y-1">
                        <label className="block text-sm font-medium text-surface-700">Appliance Type</label>
                        <select
                            value={type}
                            onChange={(e) => setType(e.target.value)}
                            className="w-full px-4 py-2 bg-white border border-surface-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all duration-200"
                        >
                            {applianceTypes.map((opt) => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                </option>
                            ))}
                        </select>
                        <p className="text-xs text-surface-500">
                            This helps us provide more accurate forecasts for this specific appliance.
                        </p>
                    </div>

                    <Button type="submit" className="w-full" disabled={!name}>
                        Save & Continue
                    </Button>
                </form>
            </CardBody>
        </Card>
    );
}
