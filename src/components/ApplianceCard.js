import React, { useState } from 'react';
import { Card, CardBody } from './ui/index';
import { AnimationWrapper } from './ui/AnimationWrapper';

export default function ApplianceCard({
    title,
    subtitle,
    icon,
    totalKwh,
    totalCost,
    children
}) {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <Card className="overflow-hidden transition-all duration-300">
            {/* 
        Mobile Header / Clickable Area 
        - On Mobile: Toggles expansion
        - On Desktop: Just a header (pointer-events-none for toggle logic if we want strict desktop behavior, but usually keeping it interactable or just static is fine. 
        Here we'll make it static on desktop and interactive on mobile via CSS/Media queries logic or just always interactive but default open on desktop?
        Better approach: Always render header. 
        Mobile: Content is hidden by default. Header toggles it.
        Desktop: Content is visible by default. Header does nothing or toggles (optional).
        
        Let's go with: 
        Mobile: Collapsed by default.
        Desktop: Expanded by default (and maybe non-collapsible or collapsible).
        
        For "Adaptive", we'll check screen size or just use CSS classes for default states? 
        React state is cleaner for "isExpanded". We can initialize based on window width or just trigger distinct layouts.
        
        Refined Strategy:
        We will use a "Mobile Summary" view that is visible only on mobile. 
        And a "Desktop Header" that is visible only on desktop.
        Actually, a shared header is better.
      */}

            {/* Mobile: Interactive Header to Toggle Expansion */}
            <div
                className="md:hidden p-4 flex items-center justify-between cursor-pointer active:bg-surface-50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-surface-100/50 text-surface-600 flex items-center justify-center">
                        {icon}
                    </div>
                    <div>
                        <h3 className="text-body-md font-semibold text-surface-900">{title}</h3>
                        <p className="text-caption text-surface-500">{subtitle}</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="text-right">
                        <p className="text-body-sm font-bold text-surface-900">₱{totalCost}</p>
                        <p className="text-caption text-surface-500">{totalKwh} kWh</p>
                    </div>
                    <svg
                        className={`w-5 h-5 text-surface-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </div>

            {/* Desktop: Content always visible. Mobile: Content conditionally visible. */}
            {/* We use a combination of CSS display for desktop and JS state for mobile to avoid hydration mismatches if possible, 
          but for simple "Details on Demand", JS state is fine. 
          
          However, to satisfy "Desktop-first = expanded", we can't easily rely on JS `window.width` during SSR/hydration without a hook.
          Simple trick: Render content always, but on mobile use CSS to hide it unless `isExpanded` class is present?
          Actually, `children` (the chart) is heavy. We might WANT to skip rendering it on mobile until expanded.
          
          Let's stick to the plan:
          Mobile: Collapsed (chart not rendered or hidden).
          Desktop: Expanded (chart rendered).
      */}

            <div className={`
        ${isExpanded ? 'block' : 'hidden'} 
        md:block 
        border-t md:border-t-0 border-surface-100 md:h-full
      `}>
                {/* On Desktop, we might want to hide the Mobile Header triggers, but we still need the styling. 
             Ideally the passed 'children' (EnergyLineChart) has its own header.
             If EnergyLineChart has its own header, we should render it fully on desktop.
             And on mobile, we render a custom summary header + the chart (without header? or with?).
             
             Let's assum children is <EnergyLineChart ... />.
             All cards in App.js use EnergyLineChart which HAS a header.
             So for Desktop: Just render {children}.
             For Mobile: Render {children} ONLY if expanded. And showing our custom summary header above.
         */}
                <div className="h-full">
                    {children}
                </div>
            </div>
        </Card>
    );
}
