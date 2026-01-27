import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Zap } from 'lucide-react';
import EnergyForecastSummary from '../components/EnergyForecastSummary';
import { generateApplianceForecast, generateActual } from '../utils/forecastUtils';

const LandingPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [dummyData, setDummyData] = useState(null);

    // Default settings for the summary view

    const tariff = 13.47;
    const budget = 300;

    // Load dummy dataset from JSON file
    useEffect(() => {
        const loadDummyData = async () => {
            try {
                const response = await fetch('/data/dummydataset.json');
                const data = await response.json();
                setDummyData(data);
            } catch (error) {
                console.error('Error loading dummy dataset:', error);
            } finally {
                setLoading(false);
            }
        };

        loadDummyData();
    }, []);

    // Logic to generate summary data (subset of DashboardPage logic)
    const calculations = useMemo(() => {
        if (loading) return null;



        let nextApplianceForecasts;
        if (dummyData?.sampleData?.['4hours']?.forecast) {
            // simplified logic for specific period
            const sample = dummyData.sampleData['4hours'].forecast;
            nextApplianceForecasts = {
                ac: sample.ac.slice(0, 4),
                ref: sample.refrigerator.slice(0, 4),
                wm: sample.washingMachine.slice(0, 4),
                ef: Array(4).fill(0).map(() => 0.15),
            }
        } else {
            nextApplianceForecasts = generateApplianceForecast(4, dummyData);
        }

        const prevActualDataTotal = generateActual(1, dummyData); // minimal previous

        const prevTotal = prevActualDataTotal.reduce((a, b) => a + b, 0);
        const nextTotal = nextApplianceForecasts.ac.reduce((a, b) => a + b, 0) +
            nextApplianceForecasts.ref.reduce((a, b) => a + b, 0) +
            nextApplianceForecasts.wm.reduce((a, b) => a + b, 0) +
            nextApplianceForecasts.ef.reduce((a, b) => a + b, 0);

        const prevCost = prevTotal * tariff;
        const nextCost = nextTotal * tariff;

        // Determine top appliance
        const acKwh = nextApplianceForecasts.ac.reduce((a, b) => a + b, 0);
        const refKwh = nextApplianceForecasts.ref.reduce((a, b) => a + b, 0);
        const efKwh = nextApplianceForecasts.ef.reduce((a, b) => a + b, 0);

        const acPhp = acKwh * tariff;
        const refPhp = refKwh * tariff;
        const efPhp = efKwh * tariff;

        const topAppliance = acPhp >= refPhp && acPhp >= efPhp ? 'Air Conditioner' :
            refPhp >= acPhp && refPhp >= efPhp ? 'Refrigerator' : 'Electric Fan';

        const budgetStatus = nextCost < budget ? 'OK' : 'At-Risk';
        const selectedPeriodText = 'Next 4 Hours';

        return {
            nextTotal,
            nextCost,
            prevTotal,
            prevCost,
            topAppliance,
            budgetStatus,
            selectedPeriodText
        };
    }, [dummyData, loading, tariff, budget]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[var(--color-bg-primary)] transition-colors duration-300">
            <div className="max-w-md w-full space-y-8 animate-fade-in flex flex-col items-center">
                <div className="text-center space-y-2">
                    <div className="inline-flex p-3 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 mb-4">
                        <Zap size={32} />
                    </div>
                    <h1 className="text-4xl font-bold tracking-tight text-[var(--color-text-primary)]">
                        Smart Energy
                    </h1>
                    <p className="text-[var(--color-text-secondary)] text-lg">
                        Intelligent forecasting for your home
                    </p>
                </div>

                {loading || !calculations ? (
                    <div className="card-base w-full h-64 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                ) : (
                    <div className="w-full">
                        <EnergyForecastSummary
                            nextKwh={calculations.nextTotal}
                            nextPhp={calculations.nextCost}
                            prevKwh={calculations.prevTotal}
                            prevPhp={calculations.prevCost}
                            actualKwh={calculations.prevTotal} // Using prev as actual for summary simplicity
                            actualPhp={calculations.prevCost}
                            topAppliance={calculations.topAppliance}
                            budgetStatus={calculations.budgetStatus}
                            selectedPeriodText={calculations.selectedPeriodText}
                        />
                    </div>
                )}

                <button
                    onClick={() => navigate('/dashboard')}
                    className="w-full group flex items-center justify-center gap-2 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                >
                    Explore Analytics
                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </button>
            </div>
        </div>
    );
};

export default LandingPage;
