/**
 * SupportPilot — Chart Helpers
 * Wraps Chart.js for analytics/engineer dashboards
 */

(function () {
  'use strict';

  /**
   * Render a doughnut chart
   */
  window.renderDoughnut = function (canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn(`Chart canvas not found: ${canvasId}`);
      return;
    }
    if (!labels || labels.length === 0) {
      console.warn(`No labels provided for chart: ${canvasId}`);
      return;
    }
    if (!data || data.length === 0) {
      console.warn(`No data provided for chart: ${canvasId}`);
      return;
    }
    try {
      const ctx = canvas.getContext('2d');
      return new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors || [
              '#2563eb','#16a34a','#d97706','#dc2626',
              '#0891b2','#7c3aed','#db2777','#84cc16'
            ],
            borderWidth: 2,
            borderColor: '#fff',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { font: { size: 11 } } },
            tooltip: { callbacks: { label: function(c) { return ` ${c.label}: ${c.raw}`; } } }
          }
        }
      });
    } catch (e) {
      console.error(`Failed to render doughnut chart ${canvasId}:`, e);
    }
  };

  /**
   * Render a bar chart
   */
  window.renderBar = function (canvasId, labels, data, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn(`Chart canvas not found: ${canvasId}`);
      return;
    }
    if (!labels || labels.length === 0) {
      console.warn(`No labels provided for chart: ${canvasId}`);
      return;
    }
    if (!data || data.length === 0) {
      console.warn(`No data provided for chart: ${canvasId}`);
      return;
    }
    try {
      const ctx = canvas.getContext('2d');
      return new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: label || 'Count',
            data: data,
            backgroundColor: color || '#2563eb',
            borderRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } },
            x: { grid: { display: false }, ticks: { font: { size: 11 } } }
          }
        }
      });
    } catch (e) {
      console.error(`Failed to render bar chart ${canvasId}:`, e);
    }
  };

  /**
   * Render a line chart (for resolution trends)
   */
  window.renderLine = function (canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn(`Chart canvas not found: ${canvasId}`);
      return;
    }
    if (!labels || labels.length === 0) {
      console.warn(`No labels provided for chart: ${canvasId}`);
      return;
    }
    if (!data || data.length === 0) {
      console.warn(`No data provided for chart: ${canvasId}`);
      return;
    }
    try {
      const ctx = canvas.getContext('2d');
      return new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: label || 'Resolved',
            data: data,
            fill: true,
            backgroundColor: 'rgba(37,99,235,0.08)',
            borderColor: '#2563eb',
            borderWidth: 2,
            tension: 0.4,
            pointBackgroundColor: '#2563eb',
            pointRadius: 3,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } },
            x: { grid: { display: false }, ticks: { font: { size: 11 }, maxRotation: 45 } }
          }
        }
      });
    } catch (e) {
      console.error(`Failed to render line chart ${canvasId}:`, e);
    }
  };

})();
