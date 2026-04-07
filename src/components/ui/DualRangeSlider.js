import React from 'react';

const DualRangeSlider = ({ min, max, value, onChange, formatLabel }) => {
    const [approaching, critical] = value;

    return (
        <div className="space-y-4">
            {/* Approaching Slider */}
            <div>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-amber-600 uppercase tracking-wider">Approaching</span>
                    <span className="text-xs font-bold text-surface-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 tabular-nums">
                        {formatLabel ? formatLabel(approaching) : approaching}
                    </span>
                </div>
                <input
                    type="range"
                    min={min}
                    max={max}
                    value={approaching}
                    onChange={(e) => {
                        const val = Math.min(Number(e.target.value), critical - 1);
                        onChange([val, critical]);
                    }}
                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
            </div>

            {/* Critical Slider */}
            <div>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-red-600 uppercase tracking-wider">Critical</span>
                    <span className="text-xs font-bold text-surface-700 bg-red-50 px-2 py-0.5 rounded border border-red-200 tabular-nums">
                        {formatLabel ? formatLabel(critical) : critical}
                    </span>
                </div>
                <input
                    type="range"
                    min={min}
                    max={max}
                    value={critical}
                    onChange={(e) => {
                        const val = Math.max(Number(e.target.value), approaching + 1);
                        onChange([approaching, val]);
                    }}
                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-red-500"
                />
            </div>
        </div>
    );
};

export default DualRangeSlider;
