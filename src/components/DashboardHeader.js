// 1. FIXED: Imported useState!
import React, { useState, useEffect } from 'react';
import { Card, IconButton } from './ui/index';
import SettingsPopover from './SettingsPopover';
// 2. FIXED: Imported the Popover component we just worked on!
import NotificationPopover from './NotificationPopover';
import { useDashboard } from '../context/DashboardContext';
import { RefreshCw, Bell } from 'lucide-react';

function DashboardHeader({
  onHelpClick,
  notifications = [],
  settings,
  onSaveSettings
}) {
  const {
    showSettings, setShowSettings,
    showNavMenu, setShowNavMenu,
  } = useDashboard();

  // 3. FIXED: Created the state that React was complaining about!
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 1024px)');
    const handleChange = () => {
      setShowSettings(false);
      setShowNavMenu(false);
      setShowNotifications(false); // Clean up if they resize screen
    };
    mq.addEventListener('change', handleChange);
    return () => mq.removeEventListener('change', handleChange);
  }, [setShowSettings, setShowNavMenu]);

  const handleLogoClick = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  const jumpOptions = [
    { value: 'tour-scenario', label: 'Scenario Simulator' },
    { value: 'tour-summary', label: 'Forecast Summary' },
    { value: 'tour-comparison', label: 'Period Comparison' },
    { value: 'tour-main-chart', label: 'Actual vs Forecast' },
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
    <header className="sticky top-0 z-40 bg-white border-b border-[#EDF2F7] px-4 py-3 mb-6 transition-all lg:hidden relative">
      <div className="flex items-center justify-between w-full">

        {/* ── LEFT: Mobile hamburger + Logo ── */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              aria-label="Open navigation menu"
              onClick={() => {
                setShowNavMenu(!showNavMenu);
                setShowSettings(false);
                setShowNotifications(false); // Close notifications if opening nav
              }}
            >
              <svg className="w-6 h-6 text-surface-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </IconButton>

            {showNavMenu && (
              <div className="absolute left-0 mt-2 w-72 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                <Card className="shadow-2xl border-surface-100 overflow-hidden">
                  <div className="p-3 border-b border-surface-50 flex items-center justify-between bg-surface-50">
                    <p className="text-body-sm font-bold text-surface-900">Navigation</p>
                    <button onClick={() => setShowNavMenu(false)} className="p-1 hover:bg-surface-200 rounded-lg text-surface-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div className="p-2">
                    {jumpOptions.map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => { handleJumpTo(opt.value); setShowNavMenu(false); }}
                        className="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-xl text-left hover:bg-surface-50 transition-colors"
                      >
                        <span className="text-body-sm font-medium text-surface-700">{opt.label}</span>
                      </button>
                    ))}
                  </div>
                  {/* User Guide — Mobile Sidebar */}
                  <div className="border-t border-surface-100 p-2">
                    <button
                      onClick={() => { if (onHelpClick) onHelpClick(); setShowNavMenu(false); }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left hover:bg-primary-50 transition-colors group"
                    >
                      <svg className="w-5 h-5 text-surface-400 group-hover:text-primary-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-body-sm font-semibold text-surface-500 group-hover:text-primary-700">User Guide</span>
                    </button>
                  </div>
                </Card>
              </div>
            )}
          </div>

          {/* Logo Override - Now using Width-based sizing! */}
          <button
            onClick={handleLogoClick}
            className="flex items-center justify-center p-0 shrink-0 transition-transform hover:scale-105"
          >
            <img
              src="/logo3.png"
              alt="Sarimax"
              className="w-[90px] sm:w-[90px] object-contain drop-shadow-sm scale-[1.3] sm:scale-[1.5] origin-left"
            />
          </button>
        </div>

        {/* ── RIGHT: Utilities ── */}
        <div className="flex items-center gap-1">

          {/* 4. FIXED: Removed the relative wrapper so the popover can escape the button bounds */}
          <IconButton
            variant="ghost"
            size="md"
            aria-label="Notifications"
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowSettings(false); // Close settings if opening notifications
              setShowNavMenu(false); // Close nav if opening notifications
            }}
          >
            <div className="relative">
              <Bell size={20} className="text-surface-600" />
              {notifications.length > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-white"></span>
              )}
            </div>
          </IconButton>

          <IconButton variant="ghost" size="md" onClick={() => window.location.reload()}>
            <RefreshCw size={20} className="text-surface-600" />
          </IconButton>

          <IconButton
            variant="ghost"
            size="md"
            onClick={() => {
              setShowSettings(!showSettings);
              setShowNavMenu(false);
              setShowNotifications(false); // Close notifications if opening settings
            }}
          >
            <svg className="w-6 h-6 text-surface-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </IconButton>
        </div>
      </div>

      {/* ── FIXED PLACEMENT POPOVERS ── */}
      {/* Moving these down here ensures they map relative to the whole header, not the tiny buttons! */}
      <div className="absolute top-full right-4 mt-2 z-50">
        <NotificationPopover
          isOpen={showNotifications}
          onClose={() => setShowNotifications(false)}
          notifications={notifications}
        />
        <SettingsPopover
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          settings={settings}
          onSave={(newSettings) => { onSaveSettings(newSettings); setShowSettings(false); }}
        />
      </div>

    </header>
  );
}

export default DashboardHeader;