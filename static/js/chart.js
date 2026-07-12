/* Chart.js Configuration Helpers & Custom Settings */

// Set global defaults for Chart.js if present in page scope
if (window.Chart) {
    Chart.defaults.font.family = "'Outfit', sans-serif";
    Chart.defaults.color = '#768390';
    console.log("Global Chart.js themes configured successfully.");
}
