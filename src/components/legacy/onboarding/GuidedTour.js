import React from 'react';
import Joyride, { STATUS } from 'react-joyride';

const GuidedTour = ({ run, onComplete }) => {
    const steps = [
        {
            target: '#tour-scenario',
            content: 'Simulation & "What-If" Analysis: Start here to test how changes in electricity rates or your household load affect your future costs. Perfect for simulation and planning.',
            placement: 'bottom',
        },
        {
            target: '#tour-summary',
            content: 'Forecast Summary: Get an immediate overview of your projected energy usage and costs for the selected period.',
            placement: 'bottom',
        },
        {
            target: '#tour-comparison',
            content: 'Period Comparison: Compare your previous usage vs the upcoming forecast. Watch for red bars—they indicate a budget risk!',
            placement: 'top',
        },
        {
            target: '#tour-main-chart',
            content: 'Actual vs Forecast: Visualize energy consumption patterns. The pulsing red indicator warns you when usage exceeds your threshold. Click "View Details" in the summary to jump here instantly.',
            placement: 'bottom',
        },
        {
            target: '#tour-appliance-breakdown',
            content: 'Appliance Breakdown: Deep dive into individual consumer consumption with real-time actual vs forecast overlays.',
            placement: 'top',
        },
        {
            target: '#tour-controls',
            content: 'Parameters & Limits: Adjust your budget limits, electricity tariff, and the forecast lookahead range.',
            placement: 'top',
        },
        {
            target: '#tour-ranking',
            content: 'Consumption Ranking: Quickly identify which appliances are costing you the most this period.',
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
