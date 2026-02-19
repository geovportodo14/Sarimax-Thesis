import React, { useState, useEffect } from 'react';

export default function SectionTabs() {
    const [activeTab, setActiveTab] = useState('overview');

    const tabs = [
        { id: 'overview', label: 'Overview', target: 'tour-summary' },
        { id: 'analytics', label: 'Analytics', target: 'charts-section' },
        { id: 'appliances', label: 'Appliances', target: 'tour-appliance-breakdown' },
        { id: 'simulator', label: 'Simulator', target: 'tour-scenario' },
    ];

    const handleTabClick = (e, tab) => {
        e.preventDefault();
        setActiveTab(tab.id);
        const element = document.getElementById(tab.target);
        if (element) {
            // Offset for sticky headers
            const headerOffset = 180;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: "smooth"
            });
        }
    };

    // Optional: Update active tab on scroll
    useEffect(() => {
        const handleScroll = () => {
            // Simple scroll spy logic can be added here
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="sticky top-[72px] z-40 bg-surface-50/95 backdrop-blur-md border-b border-surface-200 mb-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <nav className="flex space-x-8 overflow-x-auto no-scrollbar" aria-label="Tabs">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={(e) => handleTabClick(e, tab)}
                            className={`
                                whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors
                                ${activeTab === tab.id
                                    ? 'border-primary-500 text-primary-600'
                                    : 'border-transparent text-surface-500 hover:text-surface-700 hover:border-surface-300'
                                }
                            `}
                            aria-current={activeTab === tab.id ? 'page' : undefined}
                        >
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </div>
        </div>
    );
}
