import React, { forwardRef } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { IconButton } from './ui/index';
import { format } from 'date-fns';

const DateNavigator = ({ selectedDate, onDateChange, onPrevClick, onNextClick }) => {
    // Custom input component for the DatePicker to match dashboard style
    const CustomInput = forwardRef(({ value, onClick }, ref) => (
        <button
            onClick={onClick}
            ref={ref}
            type="button"
            className="flex items-center gap-2 px-6 py-2.5 bg-white rounded-xl border border-surface-200 shadow-sm hover:border-primary-400 hover:shadow-md transition-all active:scale-95 group focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
            <svg className="w-5 h-5 text-primary-500 group-hover:text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-body-md font-bold text-surface-800 tabular-nums">
                {format(selectedDate, 'MMMM d, yyyy')}
            </span>
            <svg className="w-4 h-4 text-surface-400 group-hover:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
        </button>
    ));

    return (
        <div className="flex items-center justify-center gap-4 py-6">
            <IconButton
                onClick={onPrevClick}
                variant="secondary"
                size="lg"
                aria-label="Previous day"
                className="shadow-sm hover:shadow-md active:scale-90 transition-all border border-surface-100"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
            </IconButton>

            <div className="relative">
                <DatePicker
                    selected={selectedDate}
                    onChange={(date) => onDateChange(date)}
                    customInput={<CustomInput />}
                    popperPlacement="bottom-center"
                    calendarClassName="dashboard-calendar"
                />
            </div>

            <IconButton
                onClick={onNextClick}
                variant="secondary"
                size="lg"
                aria-label="Next day"
                className="shadow-sm hover:shadow-md active:scale-90 transition-all border border-surface-100"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
            </IconButton>

            <style>{`
        .dashboard-calendar {
          border: none !important;
          border-radius: 16px !important;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
          font-family: inherit !important;
          padding: 8px !important;
        }
        .react-datepicker__header {
          background-color: white !important;
          border-bottom: 1px solid #f1f5f9 !important;
          padding-top: 12px !important;
        }
        .react-datepicker__day--selected {
          background-color: #0ea5a4 !important;
          border-radius: 10px !important;
        }
      `}</style>
        </div>
    );
};

export default DateNavigator;
