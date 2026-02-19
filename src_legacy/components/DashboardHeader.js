import React, { useState } from 'react';
import { Card, IconButton } from './ui/index';
import NotificationPopover from './NotificationPopover';
import SettingsPopover from './SettingsPopover';

function DashboardHeader({
  onHelpClick,
  notifications = [],
  settings,
  onSaveSettings
}) {
  const [showNavMenu, setShowNavMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const handleLogoClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const jumpOptions = [
    { value: 'tour-scenario', label: 'Scenario Simulator' },
    { value: 'tour-summary', label: 'Forecast Summary' },
    { value: 'tour-comparison', label: 'Period Comparison' },
    { value: 'tour-main-chart', label: 'Actual vs Forecast (Chart)' },
    { value: 'tour-appliance-breakdown', label: 'Appliance Breakdown' },
    { value: 'tour-controls', label: 'Forecast Settings' },
    { value: 'tour-ranking', label: 'Consumption Ranking' },
  ];

  const handleJumpTo = (id) => {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-surface-100 px-4 sm:px-6 lg:px-8 py-4 mb-6 animate-fade-in">
      <div className="flex items-center justify-between max-w-7xl mx-auto w-full">
        {/* Logo/Brand Section */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Burger Menu */}
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              aria-label="Open navigation menu"
              onClick={() => {
                setShowNavMenu(!showNavMenu);
                setShowNotifications(false);
                setShowSettings(false);
              }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </IconButton>

            {showNavMenu && (
              <div className="absolute left-0 mt-2 w-72 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                <Card className="shadow-2xl border-surface-100 overflow-hidden">
                  <div className="p-3 border-b border-surface-50 flex items-center justify-between bg-surface-50/50">
                    <p className="text-body-sm font-bold text-surface-900">Navigation</p>
                    <button
                      onClick={() => setShowNavMenu(false)}
                      className="p-1 hover:bg-surface-200 rounded-lg transition-colors text-surface-400"
                      aria-label="Close navigation menu"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <div className="p-2">
                    {jumpOptions
                      .map((opt) => (
                        <button
                          key={opt.value}
                          onClick={() => {
                            handleJumpTo(opt.value);
                            setShowNavMenu(false);
                          }}
                          className="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-xl text-left hover:bg-surface-50 transition-colors"
                        >
                          <span className="text-body-sm font-medium text-surface-700">{opt.label}</span>
                          <svg className="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      ))}
                  </div>
                </Card>
              </div>
            )}
          </div>

          <button
            onClick={handleLogoClick}
            className="w-auto h-12 flex items-center justify-center hover:opacity-80 transition-opacity active:scale-95"
            aria-label="Scroll to top"
          >
            <img src="/logo.png" alt="Smart Home Monitoring" className="h-full object-contain" />
          </button>
        </div>

        {/* Global Actions */}
        <div className="flex items-center gap-1 sm:gap-2">
          <IconButton variant="ghost" size="md" aria-label="Help" onClick={onHelpClick}>
            <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </IconButton>

          {/* Notifications Trigger */}
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              aria-label="Notifications"
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowNavMenu(false);
                setShowSettings(false);
              }}
            >
              <div className="relative">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                {notifications.length > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-primary-500 rounded-full border-2 border-white" />
                )}
              </div>
            </IconButton>
            <NotificationPopover
              isOpen={showNotifications}
              onClose={() => setShowNotifications(false)}
              notifications={notifications}
            />
          </div>

          {/* Settings Trigger */}
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              aria-label="Settings"
              onClick={() => {
                setShowSettings(!showSettings);
                setShowNavMenu(false);
                setShowNotifications(false);
              }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </IconButton>
            <SettingsPopover
              isOpen={showSettings}
              onClose={() => setShowSettings(false)}
              settings={settings}
              onSave={(newSettings) => {
                onSaveSettings(newSettings);
                setShowSettings(false);
              }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
