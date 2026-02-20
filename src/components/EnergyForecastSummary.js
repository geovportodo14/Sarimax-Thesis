import React from 'react';
import { Card, Button } from './ui/index';
import ColorLegend from './ColorLegend';
import { UITrendIcon } from './ui/icons';
import { Info } from 'lucide-react';

function EnergyForecastSummary({
  nextKwh,
  nextPhp,
  prevKwh,
  prevPhp,
  actualKwh,
  actualPhp,
  topAppliance,
  budgetStatus,
  selectedPeriodText,
  budget,
  hasSetBudget,
  onViewDetails,
  onSetBudget,
  thresholdApproaching = 80,
  thresholdCritical = 100
}) {
  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);
  const formatCurrency = (num) => `₱${Math.round(num).toLocaleString()}`;

  const getStatusContext = () => {
    if (!budget) return { status: 'neutral', label: 'No Budget Set', color: 'bg-surface-100', text: 'text-surface-600' };

    const ratio = nextPhp / budget;
    const criticalRatio = thresholdCritical / 100;
    const approachingRatio = thresholdApproaching / 100;

    if (ratio >= criticalRatio) {
      return {
        status: 'danger',
        label: 'Budget Exceeded',
        color: 'bg-red-100',
        text: 'text-red-600',
        gradient: 'from-red-50 to-orange-50',
        border: 'border-red-100'
      };
    } else if (ratio >= approachingRatio) {
      return {
        status: 'warning',
        label: 'Approaching Limit',
        color: 'bg-amber-100',
        text: 'text-amber-600',
        gradient: 'from-amber-50 to-orange-50',
        border: 'border-amber-100'
      };
    } else {
      return {
        status: 'success',
        label: 'Efficient Usage',
        color: 'bg-emerald-100',
        text: 'text-emerald-600',
        gradient: 'from-emerald-50 to-teal-50',
        border: 'border-emerald-100'
      };
    }
  };

  const statusContext = getStatusContext();
  const costDifference = nextPhp - prevPhp;
  const costTrend = prevPhp > 0 ? ((costDifference / prevPhp) * 100) : 0;
  const isIncreasing = costDifference > 0;

  const calculateTrend = (current, previous, suffix = 'vs last period') => {
    if (!previous || previous === 0) return null;
    const diff = ((current - previous) / previous) * 100;
    const isIncrease = diff > 0;

    // For usage, increase is red (bad), decrease is green (good)
    const colorClass = isIncrease ? 'text-red-500' : 'text-green-500';

    return (
      <span className={`${colorClass} text-sm font-medium flex items-center gap-1 mt-1`}>
        {isIncrease ? '↑' : '↓'} {Math.abs(diff).toFixed(1)}% {suffix}
      </span>
    );
  };

  const insights = [
    {
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      text: `Forecast: ${formatCurrency(nextPhp)}`,
      highlight: true,
    },
    {
      icon: UITrendIcon(isIncreasing),
      text: `${Math.abs(costTrend).toFixed(1)}% ${isIncreasing ? 'increase' : 'decrease'}`,
    },
    {
      icon: (
        <svg className="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      ),
      text: `Top: ${topAppliance}`,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between bg-emerald-50/50 p-4 rounded-xl mb-6 border border-emerald-100/50">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold text-gray-900">Forecast Summary</h2>
          <Info
            size={18}
            className="text-surface-400 cursor-help"
            title="Expected energy usage and estimated costs calculated from your past consumption habits."
          />
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-sm font-medium rounded-full flex items-center gap-1.5 shadow-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Efficient Usage
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Card 1: Energy Cost Comparison */}
        <Card className="p-6 rounded-xl shadow-sm border border-surface-100 overflow-hidden">
          <div className="flex items-center justify-between divide-x divide-surface-100 h-full">
            {/* Left Side (Primary) */}
            <div className="flex-1 pr-6">
              <p className="text-sm text-surface-500 mb-1">Expected Cost</p>
              <p className="text-3xl font-bold text-surface-900 tabular-nums">₱{Math.round(nextPhp)}</p>
              {calculateTrend(nextPhp, prevPhp, 'vs last month') || <span className="text-sm text-surface-400 mt-1">vs last period</span>}
            </div>

            {/* Right Side (Secondary) */}
            <div className="flex-1 pl-6">
              <p className="text-sm text-surface-500 mb-1">Previous Cost</p>
              <p className="text-xl font-medium text-surface-400 tabular-nums">₱{Math.round(prevPhp)}</p>
              <p className="text-sm text-surface-400 mt-1">Total billed</p>
            </div>
          </div>
        </Card>

        {/* Card 2: Energy Usage Comparison */}
        <Card className="p-6 rounded-xl shadow-sm border border-surface-100 overflow-hidden">
          <div className="flex items-center justify-between divide-x divide-surface-100 h-full">
            {/* Left Side (Primary) */}
            <div className="flex-1 pr-6">
              <p className="text-sm text-surface-500 mb-1">Current Usage</p>
              <p className="text-3xl font-bold text-surface-900 tabular-nums">{formatNumber(actualKwh)} kWh</p>
              {calculateTrend(actualKwh, nextKwh, (actualKwh > nextKwh ? 'over forecast' : 'under forecast')) || (
                <span className="text-sm text-surface-400 mt-1">vs forecast</span>
              )}
            </div>

            {/* Right Side (Secondary) */}
            <div className="flex-1 pl-6">
              <p className="text-sm text-surface-500 mb-1">Expected Usage</p>
              <p className="text-xl font-medium text-surface-400 tabular-nums">{formatNumber(nextKwh)} kWh</p>
              <p className="text-sm text-surface-400 mt-1">Based on habits</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Budget CTA (first-time users) */}
      {!hasSetBudget && (
        <div className="mb-6 rounded-2xl border border-primary-100 bg-primary-50 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="min-w-0">
            <p className="text-body-md font-semibold text-primary-700">Set your budget to unlock clearer risk alerts</p>
            <p className="text-body-sm text-primary-600/90">
              We’ll compare your forecasted cost against your budget and notify you when you’re approaching the limit.
            </p>
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={onSetBudget}
            className="sm:flex-shrink-0"
          >
            Set Budget
          </Button>
        </div>
      )}

      {/* Quick Insights */}
      <div className="mb-6">
        <h4 className="text-body-sm font-semibold text-surface-600 mb-3 uppercase tracking-wide">Quick Insights</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`flex items-center gap-3 p-3 rounded-xl ${insight.highlight ? 'bg-primary-50 border border-primary-100' : 'bg-surface-50'}`}
            >
              <span className={insight.highlight ? 'text-primary-600' : 'text-surface-500'}>
                {insight.icon}
              </span>
              <span className={`text-body-sm ${insight.highlight ? 'font-medium text-primary-700' : 'text-surface-600'}`}>
                {insight.text}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Progress (if budget provided) */}
      {budget && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-body-sm font-medium text-surface-600">Budget Progress</span>
            <span className="text-body-sm font-semibold text-surface-800">
              ₱{Math.round(nextPhp)} / ₱{budget}
            </span>
          </div>
          <div className="h-3 bg-surface-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${statusContext.status === 'danger' ? 'bg-gradient-to-r from-red-500 to-orange-500' :
                statusContext.status === 'warning' ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
                  'bg-gradient-to-r from-emerald-500 to-teal-500'
                }`}
              style={{ width: `${Math.min((nextPhp / budget) * 100, 100)}%` }}
            />
          </div>
          <p className="text-caption text-surface-500 mt-2">
            {nextPhp > budget
              ? `₱${Math.round(nextPhp - budget)} over budget`
              : `₱${Math.round(budget - nextPhp)} remaining`
            }
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          variant="primary"
          className="flex-1"
          icon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          }
          onClick={onViewDetails}
        >
          Detailed Forecast
        </Button>
        <Button
          variant="secondary"
          className="flex-1"
          icon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        >
          Risk Drivers
        </Button>
      </div>

      {/* Color Legend */}
      <ColorLegend />
    </div>
  );
}

export default EnergyForecastSummary;
