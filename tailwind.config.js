/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./links/templates/**/*.html",
    "./tenants/templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#137fec",
        "primary-dark": "#0f6fd1",
        "primary-foreground": "#e6f0ff",
        "background-light": "#f6f7f8",
        "background-dark": "#101922",
        "premium-blue": "#0f172a",
        "premium-violet": "#4c1d95",
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
        sans: ["Inter", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px",
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/container-queries")],
};
