import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#b7122a",
          container: "#db313f",
          fixed: "#ffdad8",
        },
        surface: {
          DEFAULT: "#f9f9f9",
          container: "#eeeeee",
          "container-low": "#f3f3f3",
          "container-lowest": "#ffffff",
        },
        on: {
          surface: "#1a1c1c",
          "surface-variant": "#5b403f",
          primary: "#ffffff",
        },
        outline: {
          variant: "#e4bebc",
        },
        gold: "#e9c400",
      },
      fontFamily: {
        sans: ["var(--font-jakarta)", "system-ui", "sans-serif"],
        display: ["var(--font-playfair)", "Georgia", "serif"],
      },
      borderRadius: {
        card: "12px",
      },
      boxShadow: {
        card: "0 4px 12px rgba(26, 26, 46, 0.05)",
        "card-hover": "0 8px 24px rgba(26, 26, 46, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
