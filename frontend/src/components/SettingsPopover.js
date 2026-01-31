import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Select, DualRangeSlider } from './ui/index';
import { Settings, Mail, Bell, Globe, X, Save, CheckCircle2, AlertCircle } from 'lucide-react';

const SettingsPopover = ({ isOpen, onClose, settings, onSave }) => {
    const [localSettings, setLocalSettings] = useState(settings);
    const [isValidGmail, setIsValidGmail] = useState(false);

    const validateGmail = (email) => {
        const isValid = email && email.toLowerCase().endsWith('@gmail.com');
        setIsValidGmail(!!isValid);
        return isValid;
    };

    // Sync local state when props change
    useEffect(() => {
        setLocalSettings(settings);
        if (settings.emailAddress) {
            validateGmail(settings.emailAddress);
        }
    }, [settings]);

    if (!isOpen) return null;

    const handleEmailChange = (value) => {
        const isValid = validateGmail(value);
        setLocalSettings(prev => ({
            ...prev,
            emailAddress: value,
            emailEnabled: isValid // Auto-enable if valid
        }));
    };

    const handleThresholdChange = (values) => {
        setLocalSettings(prev => ({
            ...prev,
            thresholdApproaching: values[0],
            thresholdCritical: values[1]
        }));
    };

    const handleChange = (key, value) => {
        setLocalSettings(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
            <Card className="shadow-2xl border-surface-100 overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-surface-50 flex items-center justify-between bg-surface-50/50">
                    <div className="flex items-center gap-2">
                        <Settings size={18} className="text-primary-500" />
                        <h3 className="font-bold text-surface-900 text-body-md">Dashboard Settings</h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-surface-200 rounded-lg transition-colors text-surface-400"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Content */}
                <div className="max-h-[450px] overflow-y-auto p-4 space-y-6">
                    {/* Email Alerts Section */}
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2 text-surface-900">
                                <Mail size={16} className="text-blue-500" />
                                <h4 className="text-body-sm font-bold">Gmail Notifications</h4>
                            </div>
                            {isValidGmail && (
                                <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                                    <CheckCircle2 size={12} /> Active
                                </span>
                            )}
                        </div>

                        <div className="bg-surface-50 rounded-xl p-4 border border-surface-100 space-y-3">
                            <div className="relative">
                                <Input
                                    size="sm"
                                    label="Enter your Gmail address"
                                    placeholder="yourname@gmail.com"
                                    value={localSettings.emailAddress}
                                    onChange={(e) => handleEmailChange(e.target.value)}
                                    className={isValidGmail ? 'border-emerald-500 focus:ring-emerald-500/20' : ''}
                                />
                                {localSettings.emailAddress && !isValidGmail && (
                                    <div className="flex items-center gap-1.5 mt-2 text-red-600 text-[11px] animate-in fade-in">
                                        <AlertCircle size={12} />
                                        <span>Please enter a valid @gmail.com address</span>
                                    </div>
                                )}
                                {isValidGmail && (
                                    <p className="mt-2 text-[11px] text-surface-500">
                                        You'll receive automated alerts and your dashboard link directly to this inbox.
                                    </p>
                                )}
                            </div>
                        </div>
                    </section>

                    {/* Alert Thresholds */}
                    <section>
                        <div className="flex items-center gap-2 mb-1 text-surface-900">
                            <Bell size={16} className="text-amber-500" />
                            <h4 className="text-body-sm font-bold">Alert Thresholds</h4>
                        </div>
                        <div className="px-2">
                            <p className="text-[11px] text-surface-500 mb-6">
                                Set when you want to be warned (<span className="text-amber-600 font-bold">Approaching</span>) and alerted (<span className="text-red-600 font-bold">Critical</span>).
                            </p>

                            <DualRangeSlider
                                min={0}
                                max={120}
                                value={[localSettings.thresholdApproaching, localSettings.thresholdCritical]}
                                onChange={handleThresholdChange}
                                formatLabel={(val) => `${val}%`}
                            />

                            <div className="flex justify-between mt-2 text-[10px] font-medium text-surface-400 font-mono">
                                <span>0%</span>
                                <span>120%</span>
                            </div>
                        </div>
                    </section>

                    {/* Localization */}
                    <section>
                        <div className="flex items-center gap-2 mb-3 text-surface-900">
                            <Globe size={16} className="text-emerald-500" />
                            <h4 className="text-body-sm font-bold">Localization</h4>
                        </div>
                        <div className="p-3 bg-surface-50 border border-surface-100 rounded-xl">
                            <Select
                                size="sm"
                                label="Preferred Currency"
                                value={localSettings.currency}
                                onChange={(e) => handleChange('currency', e.target.value)}
                                options={[
                                    { label: 'Philippine Peso (₱)', value: 'PHP' },
                                    { label: 'US Dollar ($)', value: 'USD' },
                                ]}
                            />
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-3 border-t border-surface-50 flex items-center justify-end gap-2 bg-surface-50/30">
                    <button
                        onClick={onClose}
                        className="px-3 py-1.5 text-body-xs font-bold text-surface-500 hover:text-surface-700 transition-colors"
                    >
                        Cancel
                    </button>
                    <Button
                        size="sm"
                        variant="primary"
                        onClick={() => onSave(localSettings)}
                        icon={<Save size={14} />}
                    >
                        Save Changes
                    </Button>
                </div>
            </Card>
        </div>
    );
};

export default SettingsPopover;
