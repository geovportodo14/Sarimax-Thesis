import React from 'react';
import { AnimationWrapper } from './ui/AnimationWrapper';

export default function RiskDriversModal({ isOpen, onClose }) {
    if (!isOpen) return null;

    const risks = [
        {
            id: 1,
            title: "High AC Dependency",
            description: "Cooling accounts for 65% of your current usage. Temperatures are higher than average this week.",
            impact: "+₱450.00",
            severity: "high", // high, medium, low
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                </svg>
            )
        },
        {
            id: 2,
            title: "Vampire Power Load",
            description: "Consistent baseline usage detected between 2 AM and 5 AM. Consider unplugging unused appliances.",
            impact: "+₱120.00",
            severity: "medium",
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            )
        },
        {
            id: 3,
            title: "Appliance Aging",
            description: "Your Refrigerator is drawing 15% more power than the manufacturer baseline. It might need maintenance.",
            impact: "+₱85.00",
            severity: "low",
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            )
        }
    ];

    const getSeverityStyles = (severity) => {
        switch (severity) {
            case 'high': return 'bg-red-50 text-red-600 border-red-100';
            case 'medium': return 'bg-amber-50 text-amber-600 border-amber-100';
            case 'low': return 'bg-blue-50 text-blue-600 border-blue-100';
            default: return 'bg-surface-50 text-surface-600 border-surface-100';
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-900/40 backdrop-blur-sm">
            <AnimationWrapper variant="slideDown">
                <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden border border-surface-100">
                    {/* Header */}
                    <div className="flex items-center justify-between p-5 border-b border-surface-100 bg-surface-50/50">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-100 text-amber-600 rounded-lg">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-heading-sm font-bold text-surface-900">Risk Drivers</h3>
                                <p className="text-caption text-surface-500">Factors pushing your bill higher</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-full transition-colors">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-5 space-y-4">
                        {risks.map((risk) => (
                            <div key={risk.id} className="flex gap-4 p-4 rounded-xl border border-surface-100 bg-white hover:border-surface-200 transition-colors shadow-sm">
                                <div className={`p-3 rounded-xl flex-shrink-0 border h-fit ${getSeverityStyles(risk.severity)}`}>
                                    {risk.icon}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className="text-body-sm font-bold text-surface-900">{risk.title}</h4>
                                        <span className={`text-caption font-bold px-2 py-0.5 rounded-md ${getSeverityStyles(risk.severity)}`}>
                                            {risk.impact}
                                        </span>
                                    </div>
                                    <p className="text-body-sm text-surface-500 leading-relaxed">
                                        {risk.description}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Footer */}
                    <div className="p-5 border-t border-surface-100 bg-surface-50 flex justify-end">
                        <button
                            onClick={onClose}
                            className="px-5 py-2.5 bg-surface-900 hover:bg-surface-800 text-white text-body-sm font-semibold rounded-xl transition-all shadow-sm"
                        >
                            Got it, thanks
                        </button>
                    </div>
                </div>
            </AnimationWrapper>
        </div>
    );
}