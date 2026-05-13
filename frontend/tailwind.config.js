/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        green:  { DEFAULT: "#16a34a", light: "#dcfce7", dark: "#14532d" },
        amber:  { DEFAULT: "#d97706", light: "#fef3c7" },
        red:    { DEFAULT: "#dc2626", light: "#fee2e2" },
        brand:  { DEFAULT: "#15803d", 50: "#f0fdf4", 900: "#14532d" },
      },
    },
  },
  plugins: [],
};
