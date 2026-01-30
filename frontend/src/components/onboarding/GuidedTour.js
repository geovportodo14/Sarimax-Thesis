import React from 'react';
import Joyride, { STATUS } from 'react-joyride';

const GuidedTour = ({ run, onComplete }) => {
    const steps = [
        {
            target: '#tour-summary',
            content: 'Forecast summary: See your projected cost and kWh consumption.',
            disableBeacon: true,
            placement: 'bottom',
        },
        {
            target: '#tour-controls',
            content: 'Adjust budget, tariff, and period here. Forecasts update instantly.',
            placement: 'top',
        },
        {
            target: '#tour-main-chart',
            content: 'Red lines mean you might exceed your budget. Keep track!',
            placement: 'bottom',
        },
        {
            target: '#tour-appliance-breakdown',
            content: 'See which appliances (Aircon, Fan, etc.) use the most power.',
            placement: 'top',
        },
        {
            target: '#tour-ranking',
            content: 'Identify top energy consumers to save efficiently.',
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
