const defaultTheme = require('tailwindcss/defaultTheme');
const forms = require('@tailwindcss/forms');
const typography = require('@tailwindcss/typography');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/app.html',
    './src/**/*.{svelte,ts,js}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f6ff',
          100: '#e7e9ff',
          200: '#ccd0ff',
          300: '#afb6ff',
          400: '#8f93ff',
          500: '#7461ff',
          600: '#5c46ff',
          700: '#4a36ee',
          800: '#3c2dc2',
          900: '#2f2293',
          950: '#1b1557',
        },
        accent: {
          sky: '#5cb7ff',
          aqua: '#42ccff',
          magenta: '#a676ff',
          amber: '#ffc073',
        },
        surface: {
          50: '#f7f8ff',
          100: '#ecefff',
          200: '#d6dcff',
          800: '#121633',
          900: '#0d1029',
          950: '#080b1d',
        },
        success: '#3dd68c',
        warning: '#f5c152',
        danger: '#ff6b6b',
      },
      fontFamily: {
        sans: ['"Inter var"', 'Inter', ...defaultTheme.fontFamily.sans],
        display: ['"Inter var"', 'Inter', ...defaultTheme.fontFamily.sans],
      },
      boxShadow: {
        glow: '0 25px 50px -12px rgba(116, 97, 255, 0.35)',
        'glow-soft': '0 20px 45px rgba(66, 204, 255, 0.25)',
      },
      backgroundImage: {
        'gradient-radial-brand': 'radial-gradient(circle at 20% 20%, rgba(166, 118, 255, 0.35), transparent 60%)',
        'gradient-radial-sky': 'radial-gradient(circle at 80% 20%, rgba(92, 183, 255, 0.28), transparent 65%)',
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 3.5s ease-in-out infinite',
        'spin-slow': 'spin 12s linear infinite',
        'fade-in': 'fade-in 0.45s ease-out both',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 0.45, filter: 'blur(0px)' },
          '50%': { opacity: 0.75, filter: 'blur(1px)' },
        },
        'fade-in': {
          '0%': { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      borderRadius: {
        brand: '22px',
      },
      dropShadow: {
        brand: ['0 20px 35px rgba(116, 97, 255, 0.35)', '0 10px 28px rgba(66, 204, 255, 0.32)'],
      },
    },
  },
  plugins: [forms, typography],
};
