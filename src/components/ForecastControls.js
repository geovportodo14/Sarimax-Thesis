import React from 'react';
import { Card, CardBody, SectionHeader, Select, Input } from './ui';

function ForecastControls({
  historyPeriod,
  forecastPeriod,
  tariff,
  budget,
  onHistoryChange,
  onForecastChange,
  onTariffChange,
  onBudgetChange,
}) {
  const historyOptions = [
    { value: 1, label: 'Past 1 Hour' },
    { value: 4, label: 'Past 4 Hours' },
    { value: 8, label: 'Past 8 Hours' },
    { value: 24, label: 'Past 24 Hours' },
  ];

  const forecastOptions = [
    { value: 1, label: 'Next 1 Hour' },
    { value: 4, label: 'Next 4 Hours' },
    { value: 8, label: 'Next 8 Hours' },
    { value: 24, label: 'Next 24 Hours' },
  ];

  return (
    <Card className="h-full">
      <CardBody>
        <SectionHeader
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          }
          title="Forecast Settings"
          subtitle="Customize your analysis"
        />

        <div className="space-y-4">
          {/* History Period */}
          <div className="flex items-center justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-body-md font-medium text-surface-700 truncate">History</span>
            </div>
            <Select
              value={historyPeriod}
              onChange={(e) => onHistoryChange(parseInt(e.target.value))}
              options={historyOptions}
              size="sm"
              selectClassName="w-auto min-w-[130px]"
            />
          </div>

          {/* Forecast Period */}
          <div className="flex items-center justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="text-body-md font-medium text-surface-700 truncate">Forecast</span>
            </div>
            <Select
              value={forecastPeriod}
              onChange={(e) => onForecastChange(parseInt(e.target.value))}
              options={forecastOptions}
              size="sm"
              selectClassName="w-auto min-w-[130px]"
            />
          </div>

          {/* Tariff Rate */}
          <div className="flex items-center justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-body-md font-medium text-surface-700 truncate">Tariff Rate</span>
            </div>
            <Input
              type="number"
              step="0.01"
              value={tariff}
              onChange={(e) => onTariffChange(parseFloat(e.target.value) || 0)}
              prefix="₱"
              size="sm"
              inputClassName="w-24 text-right"
            />
          </div>

          {/* Budget */}
          <div className="flex items-center justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="text-body-md font-medium text-surface-700 truncate">Budget</span>
            </div>
            <Input
              type="number"
              value={budget}
              onChange={(e) => onBudgetChange(parseInt(e.target.value) || 0)}
              prefix="₱"
              size="sm"
              inputClassName="w-24 text-right"
            />
          </div>
        </div>

      </CardBody>
    </Card>
  );
}

export default ForecastControls;
