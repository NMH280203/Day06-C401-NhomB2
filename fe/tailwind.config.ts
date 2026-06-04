import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#00C6E8',
          600: '#00B7D6',
          700: '#0098B3',
          800: '#087A90',
          900: '#0C6476',
          950: '#003D4D',
        },
        surface: {
          50: '#f8fafb',
          100: '#f1f5f7',
          200: '#e4eaed',
          300: '#d1dae0',
          400: '#b0bec5',
          500: '#90a4ae',
          600: '#78909c',
          700: '#546e7a',
          800: '#37474f',
          900: '#263238',
          950: '#0d1b21',
        },
        accent: {
          cyan: '#00E5FF',
          teal: '#1DE9B6',
          aqua: '#84FFFF',
          white: '#E0F7FA',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'SF Pro Display', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
      boxShadow: {
        'glow-sm': '0 0 15px rgba(0, 198, 232, 0.15)',
        'glow': '0 0 25px rgba(0, 198, 232, 0.2)',
        'glow-lg': '0 0 40px rgba(0, 198, 232, 0.25)',
        'glow-xl': '0 0 60px rgba(0, 198, 232, 0.3)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.06)',
        'glass-lg': '0 16px 48px rgba(0, 0, 0, 0.08)',
        'soft': '0 2px 16px rgba(0, 0, 0, 0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'fade-out': 'fadeOut 0.25s ease-in forwards',
        'slide-up': 'slideUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'slide-down': 'slideDown 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'slide-in-right': 'slideInRight 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'slide-in-left': 'slideInLeft 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'scale-in': 'scaleIn 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'pop-in': 'popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'pulse-dot': 'pulseDot 1.4s infinite ease-in-out both',
        'bounce-in': 'bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards',
        'shimmer': 'shimmer 2s infinite linear',
        'glow-pulse': 'glowPulse 2s infinite ease-in-out',
        'float': 'float 6s infinite ease-in-out',
        'float-slow': 'float 8s infinite ease-in-out',
        'blob': 'blob 12s infinite ease-in-out',
        'stream-glow': 'streamGlow 1.5s ease-in-out infinite',
        'tab-fade': 'tabFade 0.3s ease-out forwards',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(16px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateX(0) scale(1)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-16px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateX(0) scale(1)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.92)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        popIn: {
          '0%': { opacity: '0', transform: 'scale(0.85)' },
          '70%': { transform: 'scale(1.03)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseDot: {
          '0%, 80%, 100%': { transform: 'scale(0)' },
          '40%': { transform: 'scale(1)' },
        },
        bounceIn: {
          '0%': { opacity: '0', transform: 'scale(0.3)' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 198, 232, 0.15)' },
          '50%': { boxShadow: '0 0 35px rgba(0, 198, 232, 0.3)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        blob: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(24px, -20px) scale(1.05)' },
          '66%': { transform: 'translate(-16px, 12px) scale(0.95)' },
        },
        streamGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0, 198, 232, 0)' },
          '50%': { boxShadow: '0 0 0 3px rgba(0, 198, 232, 0.12)' },
        },
        tabFade: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
        '2xl': '24px',
        '3xl': '30px',
      },
    },
  },
  plugins: [],
}

export default config
