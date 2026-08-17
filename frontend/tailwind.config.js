/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B1E22",
        "ink-2": "#122B30",
        laterite: "#C1502E",
        "laterite-dim": "#8A3B22",
        lagoon: "#4FB3AC",
        brass: "#E3B23C",
        sand: "#F1E9D8",
        "sand-dim": "#9FB0AC",
      },
      fontFamily: {
  display: ['"Fraunces"', "serif"],
  devanagari: ['"Eczar"', "serif"],
  body: ['"Inter"', "sans-serif"],
  mono: ['"IBM Plex Mono"', "monospace"],
},
    },
  },
  plugins: [],
};