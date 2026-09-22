/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          900: '#111827',
          700: '#374151',
          500: '#6b7280',
        },
      },
    },
  },
  plugins: [],
}
