/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0F1E",
        surface: "#111827",
        card: "#1F2937",
        border: "#374151",
        primary: "#3B82F6",
        secondary: "#34D399",
        warning: "#F59E0B",
        critical: "#EF4444",
        muted: "#9CA3AF",
        sidebar: "#0B1120",
        "sidebar-muted": "#9CA3AF",
        "text-primary": "#F9FAFB",
        "text-secondary": "#9CA3AF",
      },
      fontFamily: { sans: ["Inter", "sans-serif"], mono: ["JetBrains Mono", "monospace"] },
      boxShadow: { panel: "0 12px 32px rgba(0, 0, 0, 0.18)" },
    },
  },
  plugins: [],
};