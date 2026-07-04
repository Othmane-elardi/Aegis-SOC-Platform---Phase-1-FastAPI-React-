/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: "var(--surface)",
        surface2: "var(--surface2)",
        border: "var(--border)",
        muted: "var(--text3)",
        body: "var(--text2)",
        heading: "var(--text)",
        brand: { DEFAULT: "#2dd4bf", 600: "#14b8a6" },
        crit: "#f0453f",
        high: "#f5842a",
        med: "#f5b729",
        low: "#34d399",
        info: "#5b8def",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.28)",
      },
    },
  },
  plugins: [],
};
