import React from 'react';

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
}) {
  const formatNumber = (num) => (Math.round(num * 100) / 100).toFixed(2);
  const formatCurrency = (num) => `₱${formatNumber(num)}`;

  const getStatusDotColor = () => {
    if (budgetStatus === 'OK') return 'bg-green-500';
    return 'bg-orange-500';
  };

  const mobileAlertText = `"Your forecasted energy cost for ${selectedPeriodText.toLowerCase()} is <strong>${Math.round(nextPhp)} PHP</strong>. Previous period cost: <strong>${Math.round(prevPhp)} PHP</strong>. Top-consuming appliance: <strong>${topAppliance}</strong>. Budget status: <strong>${budgetStatus}</strong>."`;

  const summaryItems = [
    {
      label: 'Next period',
      kwh: nextKwh,
      php: nextPhp,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Previous period',
      kwh: prevKwh,
      php: prevPhp,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
    },
    {
      label: 'Actual usage',
      kwh: actualKwh,
      php: actualPhp,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 h-full hover-lift animate-slide-up">
      <div className="mb-6 flex items-center gap-2">
        <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h5 className="font-bold text-xl text-gray-800">Forecast Summary</h5>
      </div>

      <div className="space-y-3 mb-6">
        {summaryItems.map((item, index) => (
          <div
            key={index}
            className={`flex justify-between items-center p-3 rounded-lg ${item.bgColor} border border-transparent hover:border-gray-200 transition-all`}
          >
            <div className="flex items-center gap-2">
              <div className={item.color}>{item.icon}</div>
              <span className="text-sm font-medium text-gray-700">{item.label}</span>
            </div>
            <div className="font-bold text-gray-800 number-counter">
              <span className="text-xs text-gray-500 font-normal mr-1">{formatNumber(item.kwh)} kWh</span>
              <span className={item.color}>{formatCurrency(item.php)}</span>
            </div>
          </div>
        ))}

        <div className="flex justify-between items-center p-3 rounded-lg bg-purple-50 border border-purple-100">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            <span className="text-sm font-medium text-gray-700">Top Appliance</span>
          </div>
          <div className="font-bold text-purple-700">{topAppliance}</div>
        </div>

        <div className={`flex justify-between items-center p-3 rounded-lg ${budgetStatus === 'OK' ? 'bg-green-50 border-green-100' : 'bg-orange-50 border-orange-100'} border`}>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusDotColor()} shadow-sm animate-pulse`}></div>
            <span className="text-sm font-medium text-gray-700">Budget Status</span>
          </div>
          <div className={`font-bold ${budgetStatus === 'OK' ? 'text-green-700' : 'text-orange-700'}`}>
            {budgetStatus}
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="font-semibold mb-3 text-gray-700 flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          Mobile Notification Preview
        </div>
        <div
          className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 border border-gray-200 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: mobileAlertText }}
        />
      </div>
    </div>
  );
}

export default EnergyForecastSummary;

