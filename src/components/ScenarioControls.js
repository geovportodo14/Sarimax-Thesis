import React from 'react';
import { useDashboard } from '../context/DashboardContext';
import { AnimationWrapper } from './ui/AnimationWrapper';

export default function ScenarioControls() {
    const {
        isScenarioMode,
        setIsScenarioMode,
        scenarioParams,
        setScenarioParams,
        tariff
    } = useDashboard();

    // Initialize scenario params when mode is toggled on if not set
    const handleToggle = () => {
        if (!isScenarioMode) {
            setScenarioParams(prev => ({
                ...prev,
                tariffAdjustment: tariff, // Start with current tariff
                loadAdjustment: 0
            }));
        }
        setIsScenarioMode(!isScenarioMode);
    };

    const handleTariffChange = (e) => {
        setScenarioParams(prev => ({
            ...prev,
            tariffAdjustment: parseFloat(e.target.value)
        }));
    };

    const handleLoadChange = (e) => {
        setScenarioParams(prev => ({
            ...prev,
            loadAdjustment: parseInt(e.target.value, 10)
        }));
    };

    return (
        <Card className={`border-l-4 ${isScenarioMode ? 'border-l-indigo-500 shadow-elevated' : 'border-l-transparent'} transition-all duration-300`}>
            <div className="p-4 sm:p-5">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isScenarioMode ? 'bg-indigo-50 text-indigo-600' : 'bg-surface-100 text-surface-400'}`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-heading-sm text-surface-900">Scenario Simulator</h3>
                            <p className="text-caption text-surface-500">Analyze "What-If" scenarios</p>
                        </div>
                    </div>

                    <button
                        onClick={handleToggle}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${isScenarioMode ? 'bg-indigo-600' : 'bg-surface-200'}`}
                    >
                        <span
                            className={`${isScenarioMode ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                        />
                    </button>
                </div>

                <AnimationWrapper variant="slideDown" layout>
                    {isScenarioMode && (
                        <div className="space-y-5 pt-2 border-t border-surface-100">
                            {/* Tariff Adjustment */}
                            <div>
                                <div className="flex justify-between mb-2">
                                    <label className="text-body-sm font-medium text-surface-700">Virtual Tariff Rate</label>
                                    <span className="text-body-sm font-bold text-indigo-600 tabular-nums">₱{scenarioParams.tariffAdjustment.toFixed(2)}</span>
                                </div>
                                <input
                                    type="range"
                                    min="5"
                                    max="30"
                                    step="0.01"
                                    value={scenarioParams.tariffAdjustment}
                                    onChange={handleTariffChange}
                                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                                <div className="flex justify-between mt-1">
                                    <span className="text-caption text-surface-400">₱5.00</span>
                                    <span className="text-caption text-surface-400">Current: ₱{tariff.toFixed(2)}</span>
                                    <span className="text-caption text-surface-400">₱30.00</span>
                                </div>
                            </div>

                            {/* Load Adjustment */}
                            <div>
                                <div className="flex justify-between mb-2">
                                    <label className="text-body-sm font-medium text-surface-700">Load Adjustment</label>
                                    <span className={`text-body-sm font-bold tabular-nums ${scenarioParams.loadAdjustment > 0 ? 'text-red-500' : scenarioParams.loadAdjustment < 0 ? 'text-emerald-500' : 'text-surface-600'}`}>
                                        {scenarioParams.loadAdjustment > 0 ? '+' : ''}{scenarioParams.loadAdjustment}%
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="-50"
                                    max="50"
                                    step="5"
                                    value={scenarioParams.loadAdjustment}
                                    onChange={handleLoadChange}
                                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                                <div className="flex justify-between mt-1">
                                    <span className="text-caption text-surface-400">-50% (Save)</span>
                                    <span className="text-caption text-surface-400">0%</span>
                                    <span className="text-caption text-surface-400">+50% (Usage)</span>
                                </div>
                            </div>

                            <div className="bg-indigo-50 rounded-lg p-3 flex gap-2 items-start">
                                <svg className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p className="text-caption text-indigo-700">
                                    Adjusting these values simulates a change in your electricity bill. Use this to plan for rate hikes or consumption reduction.
                                </p>
                            </div>
                        </div>
                    )}
                </AnimationWrapper>
            </div>
        </Card>
    );
}

// Simple internal Card components to avoid circular dependencies or complex imports if not needed
function Card({ children, className = '' }) {
    return <div className={`bg-white rounded-2xl border border-surface-100 shadow-card ${className}`}>{children}</div>;
}
