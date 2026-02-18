import React from 'react';
import { Card, CardBody, Button } from '../../components/ui';

export default function ChartTimeRangeToggle({ allTime, onToggle }) {
    return (
        <div className="flex bg-surface-100 p-1 rounded-lg">
            <button
                onClick={() => onToggle(false)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${!allTime ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-600 hover:text-surface-900'
                    }`}
            >
                Recent (24h)
            </button>
            <button
                onClick={() => onToggle(true)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${allTime ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-600 hover:text-surface-900'
                    }`}
            >
                All History
            </button>
        </div>
    );
}
