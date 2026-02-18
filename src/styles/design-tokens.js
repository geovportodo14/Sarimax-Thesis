// =============================================================================
// DESIGN TOKENS — Consistent spacing, typography, and color references
// =============================================================================
// These mirror the Tailwind config values for use in JS/React components.
// For Tailwind classes, continue using the class names directly.

export const spacing = {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
};

export const typography = {
    fontFamily: {
        sans: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        display: "'Space Grotesk', 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    },
    fontSize: {
        displayLg: '2.5rem',
        displayMd: '2rem',
        displaySm: '1.5rem',
        headingLg: '1.25rem',
        headingMd: '1.125rem',
        headingSm: '1rem',
        bodyLg: '1rem',
        bodyMd: '0.875rem',
        bodySm: '0.8125rem',
        caption: '0.75rem',
    },
};

export const colors = {
    primary: {
        50: '#ECFEFF',
        100: '#CFFAFE',
        200: '#A5F3FC',
        300: '#67E8F9',
        400: '#22D3EE',
        500: '#06B6D4',
        600: '#0891B2',
        700: '#0E7490',
        800: '#155E75',
        900: '#164E63',
    },
    chart: {
        actual: '#0EA5E9',
        forecast: '#F59E0B',
        healthy: '#10B981',
        atRisk: '#EF4444',
        stable: '#6B7280',
    },
    status: {
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#3B82F6',
    },
};

export const shadows = {
    card: '0 0 0 1px rgba(226, 232, 240, 1), 0 2px 4px rgba(15, 23, 42, 0.05)',
    cardHover: '0 0 0 1px rgba(226, 232, 240, 1), 0 10px 30px -5px rgba(15, 23, 42, 0.08)',
    elevated: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

export const borderRadius = {
    md: '0.5rem',
    lg: '0.75rem',
    xl: '0.875rem',
    '2xl': '1rem',
    '3xl': '1.25rem',
};
