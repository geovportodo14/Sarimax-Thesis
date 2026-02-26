import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getApiUrl } from '../utils/api';

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
    const [tariff, setTariff] = useState(() => {
        const saved = localStorage.getItem('dashboardTariff');
        return saved ? parseFloat(saved) : 13.47;
    });
    const [budget, setBudget] = useState(() => {
        const saved = localStorage.getItem('dashboardBudget');
        return saved ? parseFloat(saved) : 300;
    });
    const [allTime, setAllTime] = useState(true);
    const [currentDate, setCurrentDate] = useState(new Date());
    const [granularity, setGranularity] = useState(60);
    const [dummyData, setDummyData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Track if user explicitly set budget (for CTA/prompts)
    const [hasSetBudget, setHasSetBudget] = useState(() => {
        return localStorage.getItem('hasSetBudget') === 'true';
    });

    // Onboarding state
    const [showIntroduction, setShowIntroduction] = useState(false);
    const [runTour, setRunTour] = useState(false);

    // Adaptive Setup Wizard state
    const [showSetupWizard, setShowSetupWizard] = useState(false);

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

    // Shared UI overlay state — lifted to avoid duplicate instances across
    // desktop sidebar + mobile header and to allow resize-safety cleanup.
    const [showSettings, setShowSettings] = useState(false);
    const [showNavMenu, setShowNavMenu] = useState(false);

    // 🚨 THE FIX: Added the notifications overlay state right here!
    const [showNotifications, setShowNotifications] = useState(false);

    // Active section state (for sidebar/header highlights)
    const [activeSection, setActiveSection] = useState('tour-summary');


    // ===========================================================================
    // EFFECTS
    // ===========================================================================

    // Check for new user (original onboarding)
    useEffect(() => {
        const hasCompletedOnboarding = localStorage.getItem('hasCompletedOnboarding');
        if (!hasCompletedOnboarding && !loading) {
            setShowIntroduction(true);
        }
    }, [loading]);

    // Check for Adaptive Setup Wizard
    useEffect(() => {
        const hasCompletedSetup = localStorage.getItem('hasCompletedSetup');
        if (!hasCompletedSetup && !loading) {
            setShowSetupWizard(true);
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
                await fetch(getApiUrl('/api/alerts/welcome'), {
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
            localStorage.setItem('dashboardBudget', nextBudget.toString());
        }
    }, []);

    const handleTariffChange = useCallback((nextTariff) => {
        setTariff(nextTariff);
        if (Number.isFinite(nextTariff) && nextTariff > 0) {
            localStorage.setItem('dashboardTariff', nextTariff.toString());
        }
    }, []);

    // Setup Wizard Handlers
    const handleCompleteSetup = useCallback(() => {
        localStorage.setItem('hasCompletedSetup', 'true');
        setShowSetupWizard(false);
    }, []);

    const handleTriggerSetup = useCallback(() => {
        setShowSetupWizard(true);
    }, []);

    // ===========================================================================
    // VALUE
    // ===========================================================================
    // Mini-Rail / Collapsible Sidebar
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem('sidebar_collapsed');
        if (saved !== null) setIsSidebarCollapsed(JSON.parse(saved));
    }, []);

    const toggleSidebar = () => {
        setIsSidebarCollapsed(prev => {
            const newVal = !prev;
            localStorage.setItem('sidebar_collapsed', JSON.stringify(newVal));
            return newVal;
        });
    };

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
        showSetupWizard,
        settings,
        notifications,

        // Shared overlay state (desktop sidebar + mobile header share these)
        showSettings,
        setShowSettings,
        showNavMenu,
        setShowNavMenu,

        // 🚨 THE FIX: Added them to the exported Context value!
        showNotifications,
        setShowNotifications,

        // Setters
        setSelectedPeriod,
        setSelectedLookback,
        setTariff,
        handleTariffChange,
        setBudget,
        handleBudgetChange,
        setAllTime,
        setCurrentDate,
        setNotifications,
        setShowIntroduction,
        setRunTour,
        setShowSetupWizard,
        setIsScenarioMode,
        setScenarioParams,
        setForecastHorizon,
        setGranularity,

        // Scenario values
        isScenarioMode,
        scenarioParams,

        // Forecast Horizon
        forecastHorizon,
        granularity,

        // Handlers
        handleSkipIntroduction,
        handleStartTour,
        handleTourComplete,
        handleRevisitGuide,
        handlePrevDate,
        handleNextDate,
        handleSaveSettings,

        // Active section
        activeSection,
        setActiveSection,

        // Sidebar Mini-Rail
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        toggleSidebar,

        // Setup Wizard
        handleCompleteSetup,
        handleTriggerSetup
    };

    return (
        <DashboardContext.Provider value={value}>
            {children}
        </DashboardContext.Provider>
    );
};