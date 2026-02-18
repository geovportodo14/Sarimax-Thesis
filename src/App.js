import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardProvider } from './context/DashboardContext';

// Pages
import LandingPage from './pages/LandingPage';
import HowItWorksPage from './pages/HowItWorksPage';
import TariffSetupPage from './pages/TariffSetupPage';
import DeviceSetupPage from './pages/DeviceSetupPage';
import DashboardPage from './pages/DashboardPage';
import ForecastPage from './pages/ForecastPage';
import BudgetPage from './pages/BudgetPage';
import ScenariosPage from './pages/ScenariosPage';

function App() {
  return (
    <BrowserRouter>
      <DashboardProvider>
        <Routes>
          {/* Onboarding */}
          <Route path="/welcome" element={<LandingPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/setup/tariff" element={<TariffSetupPage />} />
          <Route path="/setup/device" element={<DeviceSetupPage />} />

          {/* Main App */}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/forecast" element={<ForecastPage />} />
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/welcome" replace />} />
          <Route path="*" element={<Navigate to="/welcome" replace />} />
        </Routes>
      </DashboardProvider>
    </BrowserRouter>
  );
}

export default App;
