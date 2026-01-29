import React from 'react';
import Joyride, { STATUS } from 'react-joyride';

const GuidedTour = ({ run, onComplete }) => {
    const steps = [
        {
            target: '#tour-summary',
            content: 'Here is your forecast summary. It shows you exactly how much you can expect to spend and how many kWh you might consume in your selected period.',
            disableBeacon: true,
            placement: 'bottom',
        },
        {
            target: '#tour-controls',
            content: 'Use these controls to adjust your budget, electricity tariff, and the forecast period. Smart Home Monitoring recalibrates instantly when you change these.',
            placement: 'top',
        },
        {
            target: '#tour-main-chart',
            content: 'This chart shows your actual usage (solid line) and forecasted usage (dashed line). If the line turns red, you are at risk of exceeding your budget!',
            placement: 'bottom',
        },
        {
            target: '#tour-appliance-breakdown',
            content: 'We break down the forecast by appliance. See exactly what your Aircon, Refrigerator, and Fan are contributing to your bill.',
            placement: 'top',
        },
        {
            target: '#tour-ranking',
            content: 'This ranking helps you identify your biggest energy hogs. Use this to focus your saving efforts where they matter most.',
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
                },
                tooltipContainer: {
                    textAlign: 'left',
                    borderRadius: '16px',
                    padding: '12px',
                },
                buttonNext: {
                    borderRadius: '10px',
                    fontWeight: '600',
                },
                buttonBack: {
                    fontWeight: '500',
                },
                buttonSkip: {
                    color: '#64748b',
                }
            }}
        />
    );
};

export default GuidedTour;
