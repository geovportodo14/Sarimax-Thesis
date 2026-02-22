import React, { useState } from 'react';
import { Card, CardBody, Button } from './ui/index';
import ColorLegend from './ColorLegend';
import { UITrendIcon } from './ui/icons';
import { Info } from 'lucide-react';
import RiskDriversModal from './RiskDriversModal'; // Import the new component
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
  thresholdCritical = 100,
  containerId
}) {
  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);
  const formatCurrency = (num) => `₱${Math.round(num).toLocaleString()}`;
  const [showRiskModal, setShowRiskModal] = useState(false);
  const getStatusContext = () => {
    if (!budget || budget <= 0) return { status: 'neutral', label: 'No Budget Set', color: 'bg-surface-100', text: 'text-surface-600', border: 'border-surface-200', dot: 'bg-surface-500' };

    const ratio = nextPhp / budget;
    const criticalRatio = thresholdCritical / 100;
    const approachingRatio = thresholdApproaching / 100;

    if (ratio >= criticalRatio) {
      return {
        status: 'danger',
        label: 'Budget Exceeded',
        color: 'bg-red-50',
        text: 'text-red-700',
        border: 'border-red-200',
        dot: 'bg-red-500'
      };
    } else if (ratio >= approachingRatio) {
      return {
        status: 'warning',
        label: 'Approaching Limit',
        color: 'bg-amber-50',
        text: 'text-amber-700',
        border: 'border-amber-200',
        dot: 'bg-amber-500'
      };
    } else {
      return {
        status: 'success',
        label: 'Efficient Usage',
        color: 'bg-emerald-50',
        text: 'text-emerald-700',
        border: 'border-emerald-200',
        dot: 'bg-emerald-500'
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
    <Card className="h-full" id={containerId}>
      <CardBody className="space-y-6">

        {/* DYNAMIC Status Banner */}
        <div className={`flex items-center justify-between p-4 rounded-xl mb-6 border ${statusContext.color} ${statusContext.border} bg-opacity-50`}>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-gray-900">Forecast Summary</h2>
            <Info
              size={18}
              className="text-surface-400 cursor-help"
              title="Expected energy usage and estimated costs calculated from your past consumption habits."
            />
          </div>
          <span className={`px-3 py-1 bg-white ${statusContext.text} border ${statusContext.border} text-sm font-medium rounded-full flex items-center gap-1.5 shadow-sm`}>
            <span className={`w-1.5 h-1.5 rounded-full ${statusContext.dot}`}></span>
            {statusContext.label}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Card 1: Energy Cost Comparison */}
          <div className="p-6 rounded-xl shadow-sm border border-surface-100 bg-white overflow-hidden">
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
          </div>

          {/* Card 2: Energy Usage Comparison */}
          <div className="p-6 rounded-xl shadow-sm border border-surface-100 bg-white overflow-hidden">
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
          </div>
        </div>

        {/* ==========================================
            THE UPGRADED CALL TO ACTION 
            ========================================== */}
        {!hasSetBudget && (
          <div className="mb-6 relative overflow-hidden rounded-2xl border border-primary-200 bg-gradient-to-br from-primary-50 to-white p-5 shadow-sm group transition-all hover:shadow-md">
            {/* Soft decorative background glow */}
            <div className="absolute -right-8 -top-8 w-32 h-32 bg-primary-100 rounded-full opacity-40 blur-2xl group-hover:bg-primary-200 transition-colors duration-500"></div>

            <div className="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-white rounded-xl shadow-sm text-primary-600 border border-primary-100 flex-shrink-0">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-heading-sm font-bold text-gray-900">Take control of your bill</h3>
                  <p className="text-body-sm text-surface-500 mt-1 max-w-md leading-relaxed">
                    Set a monthly energy budget to unlock personalized risk alerts and keep your consumption on track.
                  </p>
                </div>
              </div>

              <button
                onClick={onSetBudget}
                className="w-full sm:w-auto flex-shrink-0 px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-body-sm font-semibold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 group/btn"
              >
                Set My Budget
                <svg className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
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

        {/* Budget Progress (Fixed React zero render bug) */}
        {budget > 0 && (
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
            onClick={() => setShowRiskModal(true)} // 🚨 HERE IS THE FIX!
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            }
          >
            Risk Drivers
          </Button>
          <RiskDriversModal isOpen={showRiskModal} onClose={() => setShowRiskModal(false)} />
        </div>

        {/* Color Legend */}
        <ColorLegend />

      </CardBody>
    </Card>
  );
}

export default EnergyForecastSummary;