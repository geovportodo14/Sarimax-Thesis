import React from 'react';

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
  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 h-full hover-lift animate-slide-up">
      <div className="mb-6 flex items-center gap-2">
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        <h5 className="font-bold text-xl text-gray-800">Forecast Controls</h5>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-semibold text-gray-700">History Period</span>
          </div>
          <div className="flex justify-end">
            <select
              id="historySelector"
              value={historyPeriod}
              onChange={(e) => onHistoryChange(parseInt(e.target.value))}
              className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer w-full max-w-[140px]"
            >
              <option value={1}>Past 1 Hour</option>
              <option value={4}>Past 4 Hours</option>
              <option value={8}>Past 8 Hours</option>
              <option value={24}>Past 24 Hours</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span className="font-semibold text-gray-700">Forecast Period</span>
          </div>
          <div className="flex justify-end">
            <select
              id="periodSelector"
              value={forecastPeriod}
              onChange={(e) => onForecastChange(parseInt(e.target.value))}
              className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer w-full max-w-[140px]"
            >
              <option value={1}>Next 1 Hour</option>
              <option value={4}>Next 4 Hours</option>
              <option value={8}>Next 8 Hours</option>
              <option value={24}>Next 24 Hours</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-semibold text-gray-700">Tariff Rate</span>
          </div>
          <div className="flex justify-end items-center gap-1">
            <span className="text-gray-500">₱</span>
            <input
              id="tariffInput"
              type="number"
              step="0.01"
              value={tariff}
              onChange={(e) => onTariffChange(parseFloat(e.target.value) || 0)}
              className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-2 w-[100px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span className="font-semibold text-gray-700">Budget</span>
          </div>
          <div className="flex justify-end items-center gap-1">
            <span className="text-gray-500">₱</span>
            <input
              id="budgetInput"
              type="number"
              value={budget}
              onChange={(e) => onBudgetChange(parseInt(e.target.value) || 0)}
              className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-2 w-[100px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>
        </div>


      </div>

      <div id="budgetAlert" className="hidden"></div>
    </div>
  );
}

export default ForecastControls;

