import React from 'react';
import { X, Receipt } from 'lucide-react';

export default function BillBreakdownModal({ isOpen, onClose, billData }) {
    if (!isOpen || !billData) return null;

    const { breakdown, totalAmount, kwh } = billData;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col font-mono text-sm max-h-[90vh]">

                {/* Header */}
                <div className="bg-surface-50 p-4 border-b border-surface-200 flex justify-between items-center sticky top-0">
                    <div className="flex items-center gap-2">
                        <Receipt className="text-primary-600" size={20} />
                        <h3 className="font-bold text-surface-900 font-sans tracking-tight">Meralco Computation Overview</h3>
                    </div>
                    <button onClick={onClose} className="text-surface-400 hover:text-surface-700 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Receipt Content */}
                <div className="p-6 overflow-y-auto bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')]">

                    <div className="text-center mb-6">
                        <h4 className="font-bold text-lg mb-1">PROJECTED BILL</h4>
                        <p className="text-surface-500 text-xs">Based on actual MTD usage + SARIMAX forecast</p>
                        <p className="font-bold border-b-2 border-dashed border-surface-300 pb-2 mt-2">Total Consumed: {Math.round(kwh)} kWh</p>
                    </div>

                    <div className="space-y-4">
                        {/* Generation */}
                        <div className="flex justify-between">
                            <span>Generation Charge</span>
                            <span>{breakdown["Generation Charge"].toFixed(2)}</span>
                        </div>

                        {/* Transmission */}
                        <div className="flex justify-between">
                            <span>Transmission Charge</span>
                            <span>{breakdown["Transmission Charge"].toFixed(2)}</span>
                        </div>

                        {/* System Loss */}
                        <div className="flex justify-between">
                            <span>System Loss Charge</span>
                            <span>{breakdown["System Loss Charge"].toFixed(2)}</span>
                        </div>

                        {/* Distribution Tiers */}
                        <div className="border-t border-dotted border-surface-300 pt-2 space-y-1">
                            <span className="font-bold text-surface-600 block mb-1">Distribution (Meralco)</span>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Dist. Charge</span>
                                <span>{breakdown["Distribution (Meralco)"]["Distribution Charge"].toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Supply Charge</span>
                                <span>{breakdown["Distribution (Meralco)"]["Supply System Charge"].toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Metering Charge</span>
                                <span>{breakdown["Distribution (Meralco)"]["Metering Charge"].toFixed(2)}</span>
                            </div>
                        </div>

                        {/* Subsidies & Adjustments */}
                        <div className="border-t border-dotted border-surface-300 pt-2 space-y-1">
                            <span className="font-bold text-surface-600 block mb-1">Subsidies & Adjustments</span>
                            <div className="flex justify-between pl-4 text-emerald-600">
                                <span>AWAT Refund</span>
                                <span>{breakdown["Subsidies & Adjustments"]["AWAT Refund"].toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Lifeline Rate Subsidy</span>
                                <span>{breakdown["Subsidies & Adjustments"]["Lifeline Rate Subsidy"].toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Senior Citizen Subsidy</span>
                                <span>{breakdown["Subsidies & Adjustments"]["Senior Citizen Subsidy"].toFixed(2)}</span>
                            </div>
                        </div>

                        {/* Universal Charges */}
                        <div className="border-t border-dotted border-surface-300 pt-2 space-y-1">
                            <span className="font-bold text-surface-600 block mb-1">Universal Charges</span>
                            <div className="flex justify-between pl-4 text-surface-600">
                                <span>Total UC / FIT-All / GEA</span>
                                <span>
                                    {(
                                        breakdown["Universal Charges"]["UC-ME (NPC-SPUG)"] +
                                        breakdown["Universal Charges"]["UC-ME (RED-CI)"] +
                                        breakdown["Universal Charges"]["UC-EC"] +
                                        breakdown["Universal Charges"]["FIT-All"] +
                                        breakdown["Universal Charges"]["GEA-All"]
                                    ).toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* VAT */}
                        <div className="border-t border-dotted border-surface-300 pt-2 flex justify-between font-bold">
                            <span>Value Added Tax (12%)</span>
                            <span>{breakdown["Value Added Tax (12%)"].toFixed(2)}</span>
                        </div>
                    </div>

                    <div className="border-t-2 border-surface-900 mt-6 pt-4 flex justify-between items-end">
                        <div>
                            <span className="block font-bold text-lg">TOTAL AMOUNT</span>
                        </div>
                        <span className="font-bold text-2xl tracking-tighter">₱{totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>

                    <div className="mt-4 pt-3 border-t border-dashed border-surface-300">
                        <p className="text-xs text-surface-500 font-sans leading-relaxed italic">
                            {billData.rateDisclaimer || "Meralco charges change per month (per season and depends on billing). Rates used here are based on the latest available schedule and may differ from your actual bill."}
                        </p>
                    </div>

                </div>

                {/* Footer Action */}
                <div className="p-4 bg-surface-50 border-t border-surface-200">
                    <button onClick={onClose} className="w-full py-3 bg-surface-900 hover:bg-surface-800 text-white font-sans font-semibold rounded-xl transition-colors shadow-sm">
                        Close Breakdown
                    </button>
                </div>
            </div>
        </div>
    );
}
