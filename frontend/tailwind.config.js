/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#f3f5f7", surface: "#ffffff", card: "#f7f9fb", border: "#d9e0e7",
        primary: "#08708f", secondary: "#147a5b", warning: "#a96300", critical: "#bd3038",
        muted: "#667489", sidebar: "#132033", "sidebar-muted": "#9eacbd",
        "text-primary": "#172033", "text-secondary": "#526176",
      },
      fontFamily: { sans: ["Inter", "sans-serif"], mono: ["JetBrains Mono", "monospace"] },
      boxShadow: { panel: "0 1px 2px rgba(15, 23, 42, 0.06)" },
    },
  },
  plugins: [],
};