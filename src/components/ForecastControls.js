import React, { useState, useEffect } from 'react';
import { Card, CardBody, SectionHeader, Select, Input } from './ui';

function ForecastControls({
  forecastPeriod,
  tariff,
  budget,
  recommendedBudget,
  recommendedBudgetDraft,
  disabledForecast = false,
  onForecastChange,
  onTariffChange,
  onBudgetChange,
  containerId,
}) {
  // Local state for budget & tariff — only committed on "Save"
  const [localTariff, setLocalTariff] = useState(tariff);
  const [localBudget, setLocalBudget] = useState(budget);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Keep local state in sync when parent re-initializes (e.g., on page load)
  useEffect(() => { setLocalTariff(tariff); }, [tariff]);
  useEffect(() => { setLocalBudget(budget); }, [budget]);
  useEffect(() => {
    if (
      recommendedBudgetDraft &&
      Number.isFinite(recommendedBudgetDraft.value) &&
      recommendedBudgetDraft.value > 0
    ) {
      setLocalBudget(recommendedBudgetDraft.value);
      setHasUnsavedChanges(true);
    }
  }, [recommendedBudgetDraft]);

  const handleSave = () => {
    onTariffChange(localTariff === '' ? 0 : parseFloat(localTariff));
    onBudgetChange(localBudget === '' ? 0 : parseInt(localBudget));
    setHasUnsavedChanges(false);
  };

  const forecastOptions = [
    { value: 1, label: 'Forecast Window: Next 1 Hour' },
    { value: 4, label: 'Forecast Window: Next 4 Hours' },
    { value: 8, label: 'Forecast Window: Next 8 Hours' },
    { value: 24, label: 'Forecast Window: Next 24 Hours' },
  ];

  const disabledClass = disabledForecast ? 'opacity-50 pointer-events-none' : '';

  return (
    <Card className="h-full" id={containerId}>
      <CardBody>
        <SectionHeader
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          }
          title="Forecast Settings"
          subtitle={disabledForecast ? 'Viewing historical data — settings locked' : 'Model predicts 24h ahead; choose a planning window.'}
        />

        {disabledForecast && (
          <div className="flex items-center gap-2 mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
            <svg className="w-4 h-4 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-body-sm text-amber-700 font-medium">Navigate to today to adjust forecast settings.</span>
          </div>
        )}

        <div className={`space-y-4 ${disabledClass}`}>
          {/* Forecast Window */}
          <div className="flex flex-col xs:flex-row xs:items-center xs:justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-cyan-50 text-cyan-700 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-body-md font-medium text-surface-700 truncate">Forecast Window</span>
            </div>
            <Select
              value={forecastPeriod}
              onChange={(e) => onForecastChange(parseInt(e.target.value))}
              options={forecastOptions}
              size="sm"
              selectClassName="w-full xs:w-auto min-w-[130px]"
              disabled={disabledForecast}
            />
          </div>
          <p className="text-xs text-surface-500 leading-relaxed">
            The model forecasts the next 24 hours. This setting selects which upcoming window is emphasized in your totals and alerts.
          </p>
        </div>

        {/* ── Tariff & Budget with Save Button ── */}
        <div className="mt-6 pt-5 border-t border-surface-100">
          <p className="text-[11px] font-bold text-surface-400 uppercase tracking-widest mb-4">Billing Settings</p>

          <div className="space-y-4">
            {/* Tariff Rate */}
            <div className="flex flex-col xs:flex-row xs:items-center xs:justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
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
                value={localTariff}
                onChange={(e) => {
                  const val = e.target.value;
                  setLocalTariff(val === '' ? '' : parseFloat(val));
                  setHasUnsavedChanges(true);
                }}
                prefix="₱"
                size="sm"
                inputClassName="w-full xs:w-24 text-right"
              />
            </div>

            {/* Budget */}
            <div className="flex flex-col xs:flex-row xs:items-center xs:justify-between gap-4 p-4 bg-surface-50 rounded-xl border border-surface-100 hover:bg-surface-100/50 transition-colors">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <span className="text-body-md font-medium text-surface-700 truncate">Budget</span>
              </div>
              <Input
                id="budget-input"
                type="number"
                value={localBudget}
                onChange={(e) => {
                  const val = e.target.value;
                  setLocalBudget(val === '' ? '' : parseInt(val));
                  setHasUnsavedChanges(true);
                }}
                prefix="₱"
                size="sm"
                inputClassName="w-full xs:w-24 text-right"
              />
            </div>

            {Number.isFinite(recommendedBudget) && recommendedBudget > 0 && (
              <button
                onClick={() => {
                  setLocalBudget(recommendedBudget);
                  setHasUnsavedChanges(true);
                }}
                disabled={disabledForecast}
                className="w-full px-4 py-2 rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-700 text-body-sm font-semibold hover:bg-emerald-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Use Recommended Budget (₱{Math.round(recommendedBudget).toLocaleString()})
              </button>
            )}

            {/* Save Button */}
            <button
              onClick={handleSave}
              disabled={!hasUnsavedChanges}
              className={`w-full flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-body-sm font-semibold transition-all shadow-sm ${hasUnsavedChanges
                  ? 'bg-primary-600 hover:bg-primary-700 text-white cursor-pointer shadow-md'
                  : 'bg-surface-100 text-surface-400 cursor-not-allowed'
                }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {hasUnsavedChanges ? 'Save Changes' : 'Settings Saved'}
            </button>
          </div>
        </div>

      </CardBody>
    </Card>
  );
}

export default ForecastControls;
