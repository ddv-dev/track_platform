/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyan: '#37EBFF',
        blue: '#0541F0',
        darkBlue: '#0A1E64',
        darkGray: '#505569',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #37EBFF 0%, #0541F0 100%)',
        'gradient-dark': 'linear-gradient(135deg, #0A1E64 0%, #0541F0 100%)',
      },
    },
  },
  plugins: [],
}