import React, { useCallback, useEffect, useState, useRef } from 'react';

const DualRangeSlider = ({ min, max, value, onChange, formatLabel }) => {
    const [minVal, setMinVal] = useState(value[0]);
    const [maxVal, setMaxVal] = useState(value[1]);
    const minValRef = useRef(value[0]);
    const maxValRef = useRef(value[1]);
    const range = useRef(null);

    // Convert to percentage
    const getPercent = useCallback(
        (value) => Math.round(((value - min) / (max - min)) * 100),
        [min, max]
    );

    // Set width of the range
    useEffect(() => {
        const minPercent = getPercent(minVal);
        const maxPercent = getPercent(maxValRef.current);

        if (range.current) {
            range.current.style.left = `${minPercent}%`;
            range.current.style.width = `${maxPercent - minPercent}%`;
        }
    }, [minVal, getPercent]);

    useEffect(() => {
        const minPercent = getPercent(minValRef.current);
        const maxPercent = getPercent(maxVal);

        if (range.current) {
            range.current.style.width = `${maxPercent - minPercent}%`;
        }
    }, [maxVal, getPercent]);

    // Sync with props
    useEffect(() => {
        setMinVal(value[0]);
        setMaxVal(value[1]);
        minValRef.current = value[0];
        maxValRef.current = value[1];
    }, [value]);

    return (
        <div className="relative w-full h-20 flex items-center justify-center pt-8">
            {/* Visual Slider Track - Lowest Layer */}
            <div className="absolute w-full h-2 rounded-full bg-surface-200 z-0">
                <div
                    ref={range}
                    className="absolute top-0 bottom-0 h-full rounded-full bg-primary-500 z-0"
                />
            </div>

            {/* Invisible inputs - Highest Layer for interaction */}
            <input
                type="range"
                min={min}
                max={max}
                value={minVal}
                onChange={(event) => {
                    const value = Math.min(Number(event.target.value), maxVal - 1);
                    setMinVal(value);
                    minValRef.current = value;
                    onChange([value, maxVal]);
                }}
                className="thumb thumb--left absolute w-full h-0 outline-none pointer-events-none z-50"
                style={{ zIndex: minVal > max - 10 ? "50" : "40" }}
            />
            <input
                type="range"
                min={min}
                max={max}
                value={maxVal}
                onChange={(event) => {
                    const value = Math.max(Number(event.target.value), minVal + 1);
                    setMaxVal(value);
                    maxValRef.current = value;
                    onChange([minVal, value]);
                }}
                className="thumb thumb--right absolute w-full h-0 outline-none pointer-events-none z-50"
            />

            {/* Dynamic Floating Labels - Middle Layer */}
            {/* Left Label (Approaching) */}
            <div
                className="absolute -top-1 transform -translate-x-1/2 flex flex-col items-center z-30 transition-all duration-200 pointer-events-none"
                style={{ left: `${getPercent(minVal)}%` }}
            >
                <span className="text-[9px] uppercase font-bold text-amber-600 tracking-wider mb-0.5 whitespace-nowrap">
                    Approaching
                </span>
                <div className="text-[10px] font-bold text-surface-700 bg-white px-1.5 py-0.5 rounded shadow-sm border border-surface-200">
                    {formatLabel ? formatLabel(minVal) : minVal}
                </div>
            </div>

            {/* Right Label (Critical) */}
            <div
                className="absolute -top-1 transform -translate-x-1/2 flex flex-col items-center z-30 transition-all duration-200 pointer-events-none"
                style={{ left: `${getPercent(maxVal)}%` }}
            >
                <span className="text-[9px] uppercase font-bold text-red-600 tracking-wider mb-0.5 whitespace-nowrap">
                    Critical
                </span>
                <div className="text-[10px] font-bold text-surface-700 bg-white px-1.5 py-0.5 rounded shadow-sm border border-surface-200">
                    {formatLabel ? formatLabel(maxVal) : maxVal}
                </div>
            </div>

            <style>{`
        /* Cross-browser thumb styling */
        .thumb::-webkit-slider-thumb {
          -webkit-appearance: none;
          -webkit-tap-highlight-color: transparent;
          pointer-events: auto;
          height: 22px;
          width: 22px;
          border-radius: 50%;
          background-color: #ffffff;
          border: 2px solid #0ea5a4;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
          cursor: pointer;
          transform: translateY(0);
          position: relative;
          z-index: 50; /* Ensure thumb itself is high */
        }
        .thumb::-moz-range-thumb {
          pointer-events: auto;
          height: 22px;
          width: 22px;
          border-radius: 50%;
          background-color: #ffffff;
          border: 2px solid #0ea5a4;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
          cursor: pointer;
          position: relative;
          z-index: 50;
        }
        
        /* Reset track styles to invisible */
        input[type=range]::-webkit-slider-runnable-track {
          -webkit-appearance: none;
          box-shadow: none;
          border: none;
          background: transparent;
        }
        input[type=range]::-moz-range-track {
          -webkit-appearance: none;
          box-shadow: none;
          border: none;
          background: transparent;
        }
      `}</style>
        </div>
    );
};

export default DualRangeSlider;
