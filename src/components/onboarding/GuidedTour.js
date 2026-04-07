import React from 'react';
import Joyride, { STATUS } from 'react-joyride';

const GuidedTour = ({ run, onComplete }) => {
    const steps = [
        {
            target: '#tour-scenario',
            content: 'What-If Simulator: Test how changes in tariff rates or usage habits affect your forecasted energy costs. Great for budget planning.',
            placement: 'bottom',
        },
        {
            target: '#tour-summary',
            content: 'Forecast Summary: See your projected energy usage and costs at a glance for the selected period.',
            placement: 'bottom',
        },
        {
            target: '#tour-forecast-generator',
            content: 'Forecast & Optimize: Navigate to any date, then click "Forecast Next 24 Hours" to run the SARIMAX + MILP pipeline. View past optimization results in the history.',
            placement: 'bottom',
        },
        {
            target: '#tour-comparison',
            content: 'Period Comparison: Compare previous day usage vs the upcoming forecast. Red bars indicate budget risk.',
            placement: 'top',
        },
        {
            target: '#tour-main-chart',
            content: 'Actual vs Forecast Chart: Visualize hourly energy consumption patterns with actual readings and SARIMAX predictions.',
            placement: 'bottom',
        },
        {
            target: '#tour-appliance-breakdown',
            content: 'Appliance Breakdown: Dive into per-appliance consumption with actual vs forecast overlays.',
            placement: 'top',
        },
        {
            target: '#tour-controls',
            content: 'Controls: Adjust your budget, tariff rate, and forecast lookahead range.',
            placement: 'top',
        },
        {
            target: '#tour-ranking',
            content: 'Consumption Ranking: See which appliances cost you the most this period.',
            placement: 'left',
        },
    ];

    const handleJoyrideCallback = (data) => {
        const { status } = data;
        if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
            onComplete();
        }
    };

    return (
        <Joyride
            steps={steps}
            run={run}
            continuous
            scrollToFirstStep
            showProgress
            showSkipButton
            callback={handleJoyrideCallback}
            styles={{
                options: {
                    primaryColor: '#0ea5a4',
                    zIndex: 1000,
                    backgroundColor: '#ffffff',
                    textColor: '#0f172a',
                    overlayColor: 'rgba(15, 23, 42, 0.6)',
                },
                tooltipContainer: {
                    textAlign: 'left',
                    borderRadius: '16px',
                    padding: '8px',
                    fontSize: '14px',
                },
                buttonNext: {
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    padding: '8px 16px',
                },
                buttonBack: {
                    fontSize: '14px',
                    fontWeight: '500',
                    marginRight: '8px',
                },
                buttonSkip: {
                    fontSize: '14px',
                    color: '#64748b',
                }
            }}
        />
    );
};

export default GuidedTour;
