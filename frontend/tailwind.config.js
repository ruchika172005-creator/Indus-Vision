/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          sidebar: "#0B132B",
          sidebarHover: "#1C2541",
          sidebarActive: "#1E293B",
          sidebarBorder: "#1E293B",
          workspace: "#F8FAFC",
          card: "#FFFFFF",
          cardBorder: "#E2E8F0",
          textPrimary: "#0F172A",
          textSecondary: "#475569",
          textMuted: "#94A3B8",
          primary: "#2563EB",
          primaryHover: "#1D4ED8",
          primaryLight: "#EFF6FF",
          accent: "#0284C7",
          success: "#10B981",
          warning: "#F59E0B",
          orange: "#F97316",
          danger: "#EF4444",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        '2xs': "0 1px 1px 0 rgba(0, 0, 0, 0.03)"
      }
    },
  },
  plugins: [],
}
