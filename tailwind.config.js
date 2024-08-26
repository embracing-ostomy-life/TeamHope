module.exports = {
  content: [
    './team_hope/templates/*/*.html',
    './team_hope/templates/team_hope/**/*.html',
    './team_hope/templates/*.html',
    "./components/*.py",
    "./components/**/*.html",
    "./components/**/*.js",
    "./components/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        'brand-green-seafoam': '#BFE89F', // Sage
        'brand-teal-ocean': '#196E77',    // Ocean Teal
        'brand-orange-salmon': '#FF8653', // Salmon
        'brand-purple-royal': '#5C33C2',  // Royal Purple
        'brand-blue-sky': '#C0F1F7',      // Sky
        'brand-pink-bubblegum': '#FFABD6',// Bubblegum
        'brand-yellow-sunflower': '#FFD800',// Sunflower
        'brand-black-charcoal': '#282828', // Charcoal
        'brand-grey-air': '#EAEAEA',      // Air
        'brand-coral-soft': '#F96744',    // Soft Coral
        'brand-blue-pop': '#00A2D0',      // Pop Blue
      },
    },
  },
  plugins: [],
}