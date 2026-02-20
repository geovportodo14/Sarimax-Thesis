import { ChevronLeft, ChevronRight, Play, FileText, ArrowLeftRight, LineChart, LayoutGrid, Settings2, Trophy } from 'lucide-react';
import React from 'react';
import { useDashboard } from '../context/DashboardContext';

// Navigation items with icons
const NAV_ITEMS = [
    { id: 'tour-scenario', label: 'Scenario Simulator', icon: Play },
    { id: 'tour-summary', label: 'Forecast Summary', icon: FileText },
    { id: 'tour-comparison', label: 'Period Comparison', icon: ArrowLeftRight },
    { id: 'tour-main-chart', label: 'Actual vs Forecast', icon: LineChart },
    { id: 'tour-appliance-breakdown', label: 'Appliance Breakdown', icon: LayoutGrid },
    { id: 'tour-controls', label: 'Forecast Settings', icon: Settings2 },
    { id: 'tour-ranking', label: 'Consumption Ranking', icon: Trophy },
];

export default function DesktopSidebar({ onHelpClick }) {
    const {
        isSidebarCollapsed,
        toggleSidebar,
        activeSection
    } = useDashboard();

    const scrollTo = (id) => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    return (
        <>
            <aside
                className={`hidden lg:flex flex-col fixed top-0 left-0 h-screen transition-all duration-300 bg-white border-r border-surface-100 shadow-sm z-40 ${isSidebarCollapsed ? 'w-20' : 'w-64'
                    }`}
            >
                {/* Toggle Button */}
                <button
                    onClick={toggleSidebar}
                    className="absolute -right-3 top-24 z-[100] bg-white border border-gray-200 shadow-md rounded-full p-1.5 flex items-center justify-center hover:bg-gray-50 text-gray-600"
                >
                    {isSidebarCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                </button>

                <div className="h-16 flex items-center mb-6 px-4 transition-all duration-300">
                    {isSidebarCollapsed ? (
                        /* COLLAPSED: The Square Icon */
                        <div className="w-full flex justify-center">
                            <img
                                src="/icon.png"
                                alt="Icon"
                                className="h-8 w-8 object-contain"
                            />
                        </div>
                    ) : (
                        /* EXPANDED: The Full Logo */
                        <div className="flex items-center animate-in fade-in duration-500">
                            <img
                                src="/logo3.png"
                                alt="Sarimax Logo"
                                className="h-8 w-auto object-contain"
                            />
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto pt-6 pb-4 px-3 space-y-6">
                    <div>
                        {!isSidebarCollapsed && (
                            <p className="text-[11px] font-bold text-surface-400 uppercase tracking-widest px-3 mb-3">
                                Dashboard
                            </p>
                        )}
                        <ul className="space-y-1.5">
                            {NAV_ITEMS.map((item) => {
                                const Icon = item.icon;
                                const isActive = activeSection === item.id;

                                return (
                                    <li key={item.id}>
                                        <button
                                            onClick={() => scrollTo(item.id)}
                                            className={`w-full flex items-center transition-all duration-200 rounded-xl group ${isSidebarCollapsed ? 'justify-center p-3' : 'gap-3 px-3 py-2.5'
                                                } ${isActive
                                                    ? 'bg-primary-50 text-primary-700'
                                                    : 'text-surface-500 hover:bg-surface-50 hover:text-surface-900'
                                                }`}
                                            title={isSidebarCollapsed ? item.label : ''}
                                        >
                                            <Icon
                                                size={24}
                                                className={`transition-colors flex-shrink-0 ${isActive ? 'text-primary-600' : 'text-surface-400 group-hover:text-surface-600'
                                                    }`}
                                            />
                                            {!isSidebarCollapsed && (
                                                <span className={`text-body-sm font-semibold transition-opacity duration-300 ${isActive ? 'opacity-100' : 'opacity-80 group-hover:opacity-100'
                                                    }`}>
                                                    {item.label}
                                                </span>
                                            )}
                                            {isActive && !isSidebarCollapsed && (
                                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                                            )}
                                        </button>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                </nav>

                {/* Footer Actions */}
                <div className="p-4 border-t border-surface-50 space-y-2">
                    <button
                        onClick={onHelpClick}
                        className={`w-full flex items-center text-surface-500 hover:text-primary-700 hover:bg-primary-50 transition-all rounded-xl ${isSidebarCollapsed ? 'justify-center p-3' : 'gap-3 px-3 py-2.5'
                            }`}
                        title={isSidebarCollapsed ? 'User Guide' : ''}
                    >
                        <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {!isSidebarCollapsed && <span className="text-body-sm font-semibold">User Guide</span>}
                    </button>
                </div>
            </aside>
        </>
    );
}
