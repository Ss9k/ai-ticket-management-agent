/**
 * SupportPilot — Engineer Dashboard JS
 * Confirmation dialogs for resolve/close actions
 */

(function () {
  'use strict';

  // Confirm resolve
  const resolveForm = document.getElementById('resolve-form');
  if (resolveForm) {
    resolveForm.addEventListener('submit', function (e) {
      const notes = document.getElementById('resolution-notes');
      if (!notes || !notes.value.trim()) {
        e.preventDefault();
        showFlash('Please provide resolution notes before resolving.', 'warning');
        notes && notes.focus();
        return false;
      }
      if (!confirm('Mark this ticket as RESOLVED?')) {
        e.preventDefault();
        return false;
      }
    });
  }

  // Confirm close
  const closeForm = document.getElementById('close-form');
  if (closeForm) {
    closeForm.addEventListener('submit', function (e) {
      if (!confirm('Are you sure you want to CLOSE this ticket? This cannot be undone.')) {
        e.preventDefault();
        return false;
      }
    });
  }

  // Search form — prevent empty submissions
  const searchForm = document.getElementById('ticket-filter-form');
  if (searchForm) {
    // Allow empty search to reset filters
  }
})();
