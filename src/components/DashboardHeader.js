import React from 'react';

function DashboardHeader({ date, onPrevClick, onNextClick }) {
  return (
    <div className="text-center mb-10 animate-fade-in">
      <div className="flex justify-center items-center gap-4">
        <button
          onClick={onPrevClick}
          className="w-12 h-12 rounded-full bg-white shadow-lg hover:shadow-xl flex items-center justify-center text-2xl text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200 hover:scale-110 active:scale-95"
          aria-label="Previous day"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="px-6">
          <div className="font-extrabold tracking-wider text-4xl leading-tight text-gradient mb-1">
            ENERGY DASHBOARD
          </div>
          <div className="text-lg text-gray-600 mt-2 font-medium flex items-center justify-center gap-2">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {date}
          </div>
        </div>
        <button
          onClick={onNextClick}
          className="w-12 h-12 rounded-full bg-white shadow-lg hover:shadow-xl flex items-center justify-center text-2xl text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200 hover:scale-110 active:scale-95"
          aria-label="Next day"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default DashboardHeader;

