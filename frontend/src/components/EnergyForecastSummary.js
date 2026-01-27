import React from 'react';
import { Card, CardBody, StatTile, StatusBadge, Button } from './ui';

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
  onViewDetails,
}) {
  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);
  const formatCurrency = (num) => `₱${formatNumber(num)}`;

  const isAtRisk = budgetStatus === 'At-Risk';
  
  // Calculate trend
  const costDifference = nextPhp - prevPhp;
  const costTrend = prevPhp > 0 ? ((costDifference / prevPhp) * 100) : 0;
  const isIncreasing = costDifference > 0;

  // Quick insights
  const insights = [
    {
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      text: `${selectedPeriodText} forecast: ${formatCurrency(nextPhp)}`,
      highlight: true,
    },
    {
      icon: isIncreasing ? (
        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      ) : (
        <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      ),
      text: `${Math.abs(costTrend).toFixed(1)}% ${isIncreasing ? 'higher' : 'lower'} than previous period`,
    },
    {
      icon: (
        <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      ),
      text: `${topAppliance} is your top consumer`,
    },
  ];

  return (
    <Card className="overflow-hidden">
      <CardBody className="p-0">
        {/* Hero Header */}
        <div className={`px-6 py-5 ${isAtRisk ? 'bg-gradient-to-r from-red-50 to-orange-50 border-b border-red-100' : 'bg-gradient-to-r from-primary-50 to-purple-50 border-b border-primary-100'}`}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isAtRisk ? 'bg-red-100 text-red-600' : 'bg-primary-100 text-primary-600'}`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-heading-lg text-surface-900">Forecast Summary</h2>
                  <p className="text-body-sm text-surface-500">{selectedPeriodText}</p>
                </div>
              </div>
            </div>
            <StatusBadge 
              status={isAtRisk ? 'danger' : 'success'} 
              label={isAtRisk ? 'At Risk' : 'On Track'}
              size="lg"
              pulse={isAtRisk}
            />
          </div>
        </div>

        {/* Main Content */}
        <div className="p-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatTile
              label="Forecast Cost"
              value={`₱${Math.round(nextPhp)}`}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
              variant={isAtRisk ? 'danger' : 'primary'}
              size="lg"
            />
            <StatTile
              label="Forecast Usage"
              value={formatNumber(nextKwh)}
              unit="kWh"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
              variant="info"
              size="lg"
            />
            <StatTile
              label="Previous Cost"
              value={`₱${Math.round(prevPhp)}`}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
              variant="default"
            />
            <StatTile
              label="Actual Usage"
              value={formatNumber(actualKwh)}
              unit="kWh"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
              variant="success"
            />
          </div>

          {/* Quick Insights */}
          <div className="mb-6">
            <h4 className="text-body-sm font-semibold text-surface-600 mb-3 uppercase tracking-wide">Quick Insights</h4>
            <div className="space-y-2">
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
                  className={`h-full rounded-full transition-all duration-500 ${
                    isAtRisk ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-primary-500 to-purple-500'
                  }`}
                  style={{ width: `${Math.min((nextPhp / budget) * 100, 100)}%` }}
                />
              </div>
              <p className="text-caption text-surface-500 mt-2">
                {isAtRisk 
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
              View Detailed Forecast
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
              View Risk Drivers
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

export default EnergyForecastSummary;
