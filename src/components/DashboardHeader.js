import React, { useEffect } from 'react';
import { Card, IconButton } from './ui/index';
import SettingsPopover from './SettingsPopover';
import { useDashboard } from '../context/DashboardContext';
import { RefreshCw, Bell } from 'lucide-react'; // Added Bell here

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

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 1024px)');
    const handleChange = () => {
      setShowSettings(false);
      setShowNavMenu(false);
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
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#EDF2F7] px-4 py-3 mb-6 transition-all lg:hidden">
      <div className="flex items-center justify-between w-full">

        {/* ── LEFT: Mobile hamburger + Logo (Tightened gap) ── */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              aria-label="Open navigation menu"
              onClick={() => {
                setShowNavMenu(!showNavMenu);
                setShowSettings(false);
              }}
            >
              <svg className="w-6 h-6 text-surface-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </IconButton>

            {showNavMenu && (
              <div className="absolute left-0 mt-2 w-72 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                <Card className="shadow-2xl border-surface-100 overflow-hidden">
                  <div className="p-3 border-b border-surface-50 flex items-center justify-between bg-surface-50/50">
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
                </Card>
              </div>
            )}
          </div>

          {/* Logo Override */}
          <button onClick={handleLogoClick} className="flex items-center justify-center p-0 shrink-0">
            <img
              src="/logo3.png"
              alt="Sarimax"
              className="h-16 sm:h-20 w-auto object-contain"
              style={{ minWidth: '180px' }}
            />
          </button>
        </div>

        {/* ── RIGHT: Utilities ── */}
        <div className="flex items-center gap-1">
          {/* Notification Bell */}
          <IconButton variant="ghost" size="md" aria-label="Notifications">
            <div className="relative">
              <Bell size={20} className="text-surface-600" />
              {/* Red dot indicator if there are notifications */}
              {notifications.length > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-white"></span>
              )}
            </div>
          </IconButton>

          {/* Refresh Action */}
          <IconButton variant="ghost" size="md" onClick={() => window.location.reload()}>
            <RefreshCw size={20} className="text-surface-600" />
          </IconButton>

          {/* Settings Toggle */}
          <div className="relative">
            <IconButton
              variant="ghost"
              size="md"
              onClick={() => { setShowSettings(!showSettings); setShowNavMenu(false); }}
            >
              <svg className="w-6 h-6 text-surface-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </IconButton>
            <SettingsPopover
              isOpen={showSettings}
              onClose={() => setShowSettings(false)}
              settings={settings}
              onSave={(newSettings) => { onSaveSettings(newSettings); setShowSettings(false); }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;