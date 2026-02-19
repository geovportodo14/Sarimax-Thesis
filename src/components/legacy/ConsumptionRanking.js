import React from 'react';
import { Card, CardBody, SectionHeader } from './ui';
import { ApplianceIcons } from './ui/icons';

function ConsumptionRanking({ appliances }) {
  const totalKwh = appliances.reduce((sum, app) => sum + app.kwh, 0);
  const totalPhp = appliances.reduce((sum, app) => sum + app.php, 0);

  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);

  // Sort appliances by PHP (highest first) for ranking
  const sortedAppliances = [...appliances].sort((a, b) => b.php - a.php);

  // Get rank styling
  const getRankStyle = (index) => {
    const styles = [
      { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', label: '1st' },
      { bg: 'bg-surface-100', border: 'border-surface-200', text: 'text-surface-600', label: '2nd' },
      { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', label: '3rd' },
    ];
    return styles[index] || { bg: 'bg-surface-50', border: 'border-surface-100', text: 'text-surface-500', label: `${index + 1}th` };
  };

  // Get appliance icon
  const getApplianceIcon = (name) => ApplianceIcons[name] || ApplianceIcons.Default;

  return (
    <Card className="h-full">
      <CardBody>
        <SectionHeader
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
          title="Consumption Ranking"
          subtitle="Top energy consumers"
        />

        {/* Appliance List */}
        <div className="space-y-3">
          {sortedAppliances.map((appliance, index) => {
            const rankStyle = getRankStyle(index);
            const percentage = totalPhp > 0 ? (appliance.php / totalPhp) * 100 : 0;

            return (
              <div
                key={index}
                className={`relative overflow-hidden rounded-xl border ${rankStyle.border} ${rankStyle.bg} transition-all duration-200 hover:shadow-soft`}
              >
                {/* Progress bar background */}
                <div
                  className="absolute inset-y-0 left-0 bg-current opacity-5 transition-all duration-500"
                  style={{ width: `${percentage}%` }}
                />

                <div className="relative flex items-center gap-3 p-4">
                  {/* Rank Badge */}
                  <div className={`w-7 h-7 rounded-lg ${rankStyle.bg} ${rankStyle.text} flex items-center justify-center text-caption font-bold border ${rankStyle.border}`}>
                    {rankStyle.label}
                  </div>

                  {/* Icon */}
                  <div className="w-9 h-9 rounded-xl bg-white/80 flex items-center justify-center text-surface-600 shadow-inner-soft">
                    {getApplianceIcon(appliance.name)}
                  </div>

                  {/* Name */}
                  <div className="flex-1 min-w-0">
                    <p className="text-body-md font-semibold text-surface-800 truncate">
                      {appliance.name}
                    </p>
                    <p className="text-caption text-surface-500">
                      {percentage.toFixed(1)}% of total
                    </p>
                  </div>

                  {/* Values */}
                  <div className="text-right flex-shrink-0">
                    <p className="text-body-md font-bold text-surface-800 tabular-nums">
                      ₱{Math.round(appliance.php)}
                    </p>
                    <p className="text-caption text-surface-500 tabular-nums">
                      {formatNumber(appliance.kwh)} kWh
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Total Section */}
        <div className="mt-5 pt-5 border-t border-surface-100">
          <div className="flex items-center justify-between p-4 bg-primary-50 rounded-xl border border-primary-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-primary-100 text-primary-600 flex items-center justify-center">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="text-body-md font-semibold text-surface-800">Total</span>
            </div>
            <div className="text-right">
              <p className="text-heading-md font-bold text-primary-700 tabular-nums">
                ₱{Math.round(totalPhp)}
              </p>
              <p className="text-body-sm text-surface-500 tabular-nums">
                {formatNumber(totalKwh)} kWh
              </p>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

export default ConsumptionRanking;
