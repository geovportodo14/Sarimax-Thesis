/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Meralco Brand Color System (merged with Tailwind scales for global index.css compatibility)
        primary: {
          ...colors.orange,
          DEFAULT: '#FF6B00', // Meralco Solar Orange
          hover: '#E65D00',
        },
        accent: {
          ...colors.slate,
          DEFAULT: '#0F172A', // Meralco Brand Navy
          light: '#1E293B',
        },
        navy: {
          DEFAULT: '#0F172A',
        },
        sky: {
          ...colors.sky,
          DEFAULT: '#0284C7', // Meralco Data Blue
        },
        surface: {
          ...colors.slate,
          DEFAULT: '#FFFFFF', // Clean White
          muted: '#F8FAFC',   // Very Light Gray
          border: '#E2E8F0',
          800: '#1E293B',
        },
        status: {
          success: colors.green[500],
          warning: colors.yellow[500],
          danger: colors.red[500],
          info: colors.blue[500],
        }
      },
      fontFamily: {
        display: ['ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [],
}