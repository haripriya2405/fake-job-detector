/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#050a08',
          obsidian: '#030806',
          secondary: '#07100c',
        },
        surface: {
          DEFAULT: '#0a1410',
          elevated: '#0f1c17',
          card: '#08120e',
        },
        border: {
          DEFAULT: 'rgba(160, 255, 210, 0.10)',
          subtle: 'rgba(255, 255, 255, 0.06)',
          strong: 'rgba(160, 255, 210, 0.18)',
          hairline: 'rgba(255, 255, 255, 0.08)',
        },
        emerald: {
          DEFAULT: '#10B981',
          bright: '#34D399',
          deep: '#047857',
          glow: 'rgba(16, 185, 129, 0.25)',
        },
        skywash: '#38bdf8',
        mist: '#9AAEA5',
        fog: '#70817A',
        frost: '#E7F5EF',
        ink: '#050a08',
        'ink-2': '#07100c',
        'ink-3': '#0a1410',
        danger: {
          DEFAULT: '#EF4444',
          bright: '#FF5B5B',
          muted: 'rgba(239, 68, 68, 0.15)',
        },
        warning: {
          DEFAULT: '#F59E0B',
          muted: 'rgba(245, 158, 11, 0.15)',
        },
        info: {
          DEFAULT: '#38BDF8',
          muted: 'rgba(56, 189, 248, 0.15)',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.6), 0 2px 6px -1px rgba(0, 0, 0, 0.4)',
        'hairline-inset': 'inset 0 0 0 1px rgba(255, 255, 255, 0.08)',
        'emerald-glow': '0 0 35px -5px rgba(16, 185, 129, 0.3)',
        'emerald-button': '0 10px 25px -5px rgba(16, 185, 129, 0.35)',
        'glass-card': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
    },
  },
  plugins: [],
}
