import React, { useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogoClick = () => {
    navigate('/dashboard');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navLinks = [
    { to: '/dashboard', label: 'Overview', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z' },
    { to: '/forecast', label: 'Forecast', icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' },
    { to: '/scenarios', label: 'Scenarios', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
    { to: '/budget', label: 'Budget', icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];

  return (
<<<<<<< Updated upstream
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-surface-100 animate-fade-in mb-6">
      <div className="px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto w-full">
          {/* Logo/Brand Section */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Burger Menu (Mobile Only) */}
            <div className="relative lg:hidden">
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
=======
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-surface-100 px-4 sm:px-6 lg:px-8 py-4 mb-6 animate-fade-in">
      <div className="flex items-center justify-between max-w-7xl mx-auto w-full">
        {/* Logo/Brand Section */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Burger Menu (Mobile Only - visible below lg) */}
          <div className="relative lg:hidden">
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
>>>>>>> Stashed changes

              {showNavMenu && (
                <div className="absolute left-0 mt-2 w-72 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                  <Card className="shadow-2xl border-surface-100 overflow-hidden">
                    <div className="p-3 border-b border-surface-50 flex items-center justify-between bg-surface-50/50">
                      <p className="text-body-sm font-bold text-surface-900">Menu</p>
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

                    <div className="p-2 space-y-1">
                      {navLinks.map((link) => (
                        <NavLink
                          key={link.to}
                          to={link.to}
                          onClick={() => setShowNavMenu(false)}
                          className={({ isActive }) => `
                            w-full flex items-center gap-3 px-3 py-2 rounded-xl text-left transition-colors
                            ${isActive ? 'bg-primary-50 text-primary-700 font-medium' : 'text-surface-700 hover:bg-surface-50'}
                          `}
                        >
                          <svg className={`w-5 h-5 ${location.pathname === link.to ? 'text-primary-500' : 'text-surface-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={link.icon} />
                          </svg>
                          <span className="text-body-sm">{link.label}</span>
                        </NavLink>
                      ))}
                      <div className="h-px bg-surface-100 my-2" />
                      <button
                        onClick={() => { onHelpClick(); setShowNavMenu(false); }}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-left hover:bg-surface-50 transition-colors text-surface-700"
                      >
                        <svg className="w-5 h-5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-body-sm">Help & Guide</span>
                      </button>
                    </div>
                  </Card>
                </div>
              )}
            </div>

            <button
              onClick={handleLogoClick}
              className="w-auto h-12 flex items-center justify-center hover:opacity-80 transition-opacity active:scale-95"
              aria-label="Go to Dashboard"
            >
              <img src="/logo.png" alt="Smart Home Monitoring" className="h-full object-contain" />
            </button>
          </div>

<<<<<<< Updated upstream
          {/* Desktop Navigation Tabs */}
          <div className="hidden lg:flex items-center gap-1 bg-surface-100/50 p-1 rounded-xl">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `
                    px-4 py-2 rounded-lg text-body-sm font-medium transition-all duration-200
                    ${isActive
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-surface-600 hover:text-surface-900 hover:bg-white/50'}
                  `}
              >
                {link.label}
              </NavLink>
            ))}
          </div>

          {/* Global Actions */}
          <div className="flex items-center gap-1 sm:gap-2">
            <div className="hidden sm:block">
              <IconButton variant="ghost" size="md" aria-label="Help" onClick={onHelpClick}>
                <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </IconButton>
            </div>

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
=======
          <button
            onClick={handleLogoClick}
            className="w-auto h-12 flex items-center justify-center hover:opacity-80 transition-opacity active:scale-95 lg:hidden"
            aria-label="Scroll to top"
          >
            <img src="/logo.png" alt="Smart Home Monitoring" className="h-full object-contain" />
          </button>

          {/* Device Status Indicator */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-full cursor-help group relative">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-emerald-700">Live</span>

            {/* Tooltip */}
            <div className="absolute top-full left-0 mt-2 w-48 p-2 bg-slate-800 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              Data verified from IoT Sensor [DEV-001]. Connection secure.
>>>>>>> Stashed changes
            </div>
          </div>
        </div>

<<<<<<< Updated upstream
        {/* Mobile Navigation Tabs (Bottom scrolling bar) */}
        <div className="lg:hidden mt-4 -mx-4 px-4 overflow-x-auto scrollbar-hide">
          <div className="flex gap-2">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `
                    flex-shrink-0 px-4 py-2 rounded-lg text-body-sm font-medium whitespace-nowrap transition-colors
                    ${isActive
                    ? 'bg-primary-50 text-primary-700 border border-primary-100'
                    : 'bg-surface-50 text-surface-600 border border-surface-100'}
                  `}
              >
                {link.label}
              </NavLink>
            ))}
=======
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

          {/* Settings Trigger (Mobile Only - moved to Sidebar on Desktop) */}
          <div className="relative lg:hidden">
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
>>>>>>> Stashed changes
          </div>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
