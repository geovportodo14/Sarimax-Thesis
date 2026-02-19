import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function UserGuideModal({ isOpen, onClose }) {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Detailed Overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm"
                    />

                    {/* Modal Panel */}
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.95, opacity: 0 }}
                        className="relative w-full max-w-md overflow-hidden rounded-2xl bg-white p-6 shadow-xl z-50"
                    >
                        <h3 className="text-lg font-medium leading-6 text-gray-900">
                            Dashboard User Guide
                        </h3>
                        <div className="mt-2">
                            <p className="text-sm text-gray-500">
                                Welcome to your Energy Forecast Dashboard! Here you can monitor your energy consumption, view forecasts, and simulate different usage scenarios.
                            </p>
                            <ul className="mt-4 space-y-2 text-sm text-gray-600 list-disc pl-5">
                                <li><strong>Forecast Summary:</strong> View your predicted energy usage and costs.</li>
                                <li><strong>Appliance Analytics:</strong> Breakdown of energy usage by appliance.</li>
                                <li><strong>Scenario Simulator:</strong> Adjust parameters to see how they affect your forecast.</li>
                            </ul>
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button
                                type="button"
                                className="inline-flex justify-center rounded-lg border border-transparent bg-primary-100 px-4 py-2 text-sm font-medium text-primary-900 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                                onClick={onClose}
                            >
                                Got it, thanks!
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
