// ---------- Time-of-day greeting ----------
// Swaps "Welcome back" for a friendlier greeting based on the visitor's
// own local time (not the server's), so it feels personal.
const greetingEl = document.getElementById("dashGreeting");

if (greetingEl) {
  const hour = new Date().getHours();
  let timeGreeting = "Good evening";
  if (hour < 12) timeGreeting = "Good morning";
  else if (hour < 17) timeGreeting = "Good afternoon";

  // Keep whatever name was already server-rendered after "Welcome back",
  // just swap the "Welcome back" part for the time-based greeting.
  greetingEl.textContent = greetingEl.textContent.replace("Welcome back", timeGreeting);
}

// ---------- Score trend chart ----------
// Only runs if the dashboard actually has a chart canvas and Chart.js loaded
// (both are only included in dashboard.html when there's enough data to show).
const chartCanvas = document.getElementById("scoreTrendChart");
const chartDataEl = document.getElementById("scoreTrendData");

if (chartCanvas && chartDataEl && window.Chart) {
  const trend = JSON.parse(chartDataEl.textContent);

  new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: trend.map((point) => point.date),
      datasets: [
        {
          label: "ATS Score",
          data: trend.map((point) => point.score),
          borderColor: "#6e44e8",
          backgroundColor: "rgba(110, 68, 232, 0.08)",
          borderWidth: 2,
          pointBackgroundColor: "#6e44e8",
          pointRadius: 4,
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { callback: (value) => value + "%" },
          grid: { color: "#f0edfa" },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });
}
