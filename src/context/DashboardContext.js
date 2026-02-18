import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const DashboardContext = createContext();

export const useDashboard = () => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error('useDashboard must be used within a DashboardProvider');
    }
    return context;
};

export const DashboardProvider = ({ children }) => {
    // ===========================================================================
    // STATE
    // ===========================================================================
    const [selectedPeriod, setSelectedPeriod] = useState(1);
    const [selectedLookback, setSelectedLookback] = useState(1);
    const [tariff, setTariff] = useState(13.47);
    const [budget, setBudget] = useState(300);
    const [allTime, setAllTime] = useState(true);
    const [currentDate, setCurrentDate] = useState(new Date());
    const [dummyData, setDummyData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Track if user explicitly set budget (for CTA/prompts)
    const [hasSetBudget, setHasSetBudget] = useState(() => {
        return localStorage.getItem('hasSetBudget') === 'true';
    });

    // Onboarding state
    const [showIntroduction, setShowIntroduction] = useState(false);
    const [runTour, setRunTour] = useState(false);

    // Settings & Notifications state
    const [settings, setSettings] = useState(() => {
        const saved = localStorage.getItem('dashboardSettings');
        return saved ? JSON.parse(saved) : {
            emailEnabled: false,
            emailAddress: '',
            thresholdApproaching: 80,
            thresholdCritical: 100,
            currency: 'PHP',
        };
    });
    const [notifications, setNotifications] = useState([]);

    // Scenario Mode state
    const [isScenarioMode, setIsScenarioMode] = useState(false);
    const [scenarioParams, setScenarioParams] = useState({
        tariffAdjustment: 13.47, // Default to base tariff
        loadAdjustment: 0,       // Percent change (-50 to +50)
    });

    // Forecast Horizon state (Thesis 3.6.4.C)
    const [forecastHorizon, setForecastHorizon] = useState(24); // 6, 12, or 24 hours


    // ===========================================================================
    // EFFECTS
    // ===========================================================================

    // Check for new user
    useEffect(() => {
        const hasCompletedOnboarding = localStorage.getItem('hasCompletedOnboarding');
        if (!hasCompletedOnboarding && !loading) {
            setShowIntroduction(true);
        }
    }, [loading]);

    // Load dummy dataset
    useEffect(() => {
        const loadDummyData = async () => {
            try {
                const response = await fetch('/data/dummydataset.json');
                const data = await response.json();
                setDummyData(data);

                if (data.settings) {
                    if (data.settings.defaultTariff) setTariff(data.settings.defaultTariff);
                    if (data.settings.defaultBudget) setBudget(data.settings.defaultBudget);
                }
            } catch (error) {
                console.error('Error loading dummy dataset:', error);
            } finally {
                setLoading(false);
            }
        };

        loadDummyData();
    }, []);

    // ===========================================================================
    // HANDLERS
    // ===========================================================================

    const handleSkipIntroduction = useCallback(() => {
        setShowIntroduction(false);
        localStorage.setItem('hasCompletedOnboarding', 'true');
    }, []);

    const handleStartTour = useCallback(() => {
        setShowIntroduction(false);
        setRunTour(true);
    }, []);

    const handleTourComplete = useCallback(() => {
        setRunTour(false);
        localStorage.setItem('hasCompletedOnboarding', 'true');
    }, []);

    const handleRevisitGuide = useCallback(() => {
        setShowIntroduction(true);
    }, []);

    const handlePrevDate = useCallback(() => {
        setCurrentDate(prev => {
            const newDate = new Date(prev);
            newDate.setDate(newDate.getDate() - 1);
            return newDate;
        });
    }, []);

    const handleNextDate = useCallback(() => {
        setCurrentDate(prev => {
            const newDate = new Date(prev);
            newDate.setDate(newDate.getDate() + 1);
            return newDate;
        });
    }, []);

    const handleSaveSettings = useCallback(async (newSettings) => {
        const emailChanged = newSettings.emailAddress !== settings.emailAddress && newSettings.emailAddress.endsWith('@gmail.com');

        setSettings(newSettings);
        localStorage.setItem('dashboardSettings', JSON.stringify(newSettings));

        if (emailChanged) {
            try {
                await fetch('/api/alerts/welcome', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: newSettings.emailAddress })
                });
                console.log('Welcome email triggered for:', newSettings.emailAddress);
            } catch (error) {
                console.error('Failed to trigger welcome email:', error);
            }
        }
    }, [settings.emailAddress]);

    const handleBudgetChange = useCallback((nextBudget) => {
        setBudget(nextBudget);
        if (Number.isFinite(nextBudget) && nextBudget > 0) {
            setHasSetBudget(true);
            localStorage.setItem('hasSetBudget', 'true');
        }
    }, []);

    // ===========================================================================
    // APP PHASE & ONBOARDING
    // ===========================================================================
    const [onboardingComplete, _setOnboardingComplete] = useState(() => {
        return localStorage.getItem('hasCompletedOnboarding') === 'true';
    });

    // Mock baseline data collection (in a real app, this would come from API)
    const [baselineDays, setBaselineDays] = useState(() => {
        return Number(localStorage.getItem('baselineDays')) || 0;
    });

    const setOnboardingComplete = useCallback((val) => {
        _setOnboardingComplete(val);
        localStorage.setItem('hasCompletedOnboarding', String(val));
        if (val) {
            setShowIntroduction(false);
        }
    }, []);

    // Derived State
    const appPhase = !onboardingComplete ? 'no_data' : (baselineDays < 30 ? 'learning' : 'active');
    const budgetUnlocked = baselineDays >= 30;

    // Debug helper to simulate days passing
    const simulateDaysPassing = useCallback((days) => {
        const newDays = baselineDays + days;
        setBaselineDays(newDays);
        localStorage.setItem('baselineDays', String(newDays));
    }, [baselineDays]);


    // ===========================================================================
    // VALUE
    // ===========================================================================
    const value = {
        // State
        selectedPeriod,
        selectedLookback,
        tariff,
        budget,
        hasSetBudget,
        allTime,
        currentDate,
        dummyData,
        loading,
        showIntroduction,
        runTour,
        settings,
        notifications,

        // New State
        onboardingComplete,
        baselineDays,
        appPhase,
        budgetUnlocked,

        // Setters
        setSelectedPeriod,
        setSelectedLookback,
        setTariff,
        setBudget,
        handleBudgetChange,
        setAllTime,
        setCurrentDate,
        setNotifications,
        setShowIntroduction,
        setRunTour,
        setIsScenarioMode,
        setScenarioParams,
        setForecastHorizon,
        setOnboardingComplete,
        simulateDaysPassing,

        // Scenario values
        isScenarioMode,
        scenarioParams,

        // Forecast Horizon
        forecastHorizon,

        // Handlers
        handleSkipIntroduction,
        handleStartTour,
        handleTourComplete,
        handleRevisitGuide,
        handlePrevDate,
        handleNextDate,
        handleSaveSettings
    };

    return (
        <DashboardContext.Provider value={value}>
            {children}
        </DashboardContext.Provider>
    );
};
