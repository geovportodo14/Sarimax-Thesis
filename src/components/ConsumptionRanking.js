import React from 'react';

function ConsumptionRanking({ appliances }) {
  const totalKwh = appliances.reduce((sum, app) => sum + app.kwh, 0);
  const totalPhp = appliances.reduce((sum, app) => sum + app.php, 0);

  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);

  const getRankBadge = (index) => {
    const badges = [
      { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '🥇' },
      { bg: 'bg-gray-100', text: 'text-gray-800', icon: '🥈' },
      { bg: 'bg-orange-100', text: 'text-orange-800', icon: '🥉' },
    ];
    return badges[index] || { bg: 'bg-blue-100', text: 'text-blue-800', icon: `${index + 1}` };
  };

  // Sort appliances by PHP (highest first) for ranking
  const sortedAppliances = [...appliances].sort((a, b) => b.php - a.php);

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 h-full hover-lift animate-slide-up">
      <div className="mb-6 flex items-center gap-2">
        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h5 className="font-bold text-xl text-gray-800">Consumption Ranking</h5>
      </div>

      <div className="space-y-3 mb-4">
        {sortedAppliances.map((appliance, index) => {
          const badge = getRankBadge(index);
          return (
            <div
              key={index}
              className="flex justify-between items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
            >
              <div className="flex items-center gap-3 flex-1">
                <div className={`w-8 h-8 ${badge.bg} ${badge.text} rounded-full flex items-center justify-center font-bold text-sm shadow-sm`}>
                  {badge.icon}
                </div>
                <div className="font-semibold text-gray-800">{appliance.name}</div>
              </div>
              <div className="flex gap-2">
                <span className="inline-flex items-center px-3 py-1.5 rounded-full font-semibold text-xs whitespace-nowrap bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 shadow-sm">
                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  {formatNumber(appliance.kwh)} kWh
                </span>
                <span className="inline-flex items-center px-3 py-1.5 rounded-full font-semibold text-xs whitespace-nowrap bg-gradient-to-r from-red-100 to-pink-100 text-red-800 shadow-sm">
                  <span className="mr-1">₱</span>
                  {Math.round(appliance.php)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t-2 border-gray-200">
        <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
          <div className="font-bold text-gray-800 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Total
          </div>
          <div className="flex gap-2">
            <span className="inline-flex items-center px-3 py-1.5 rounded-full font-bold text-sm whitespace-nowrap bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-md">
              {formatNumber(totalKwh)} kWh
            </span>
            <span className="inline-flex items-center px-3 py-1.5 rounded-full font-bold text-sm whitespace-nowrap bg-gradient-to-r from-red-500 to-pink-600 text-white shadow-md">
              ₱{Math.round(totalPhp)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConsumptionRanking;

