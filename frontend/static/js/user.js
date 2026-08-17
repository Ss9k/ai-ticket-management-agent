/**
 * SupportPilot — User Dashboard JS
 * Handles AI query, result display, and ticket creation flow
 */

(function () {
  'use strict';

  let _lastAiResponse = '';

  // ── Ask AI ──────────────────────────────────────────────────────────────
  const askBtn = document.getElementById('btn-ask-ai');
  if (askBtn) {
    askBtn.addEventListener('click', function () {
      const title = document.getElementById('problem-title').value.trim();
      const desc = document.getElementById('problem-description').value.trim();

      if (!title) { showFlash('Please enter a problem title.', 'warning'); return; }
      if (!desc)  { showFlash('Please describe your problem.', 'warning'); return; }

      Loader.show('Analyzing your problem...');
      askBtn.disabled = true;
      document.getElementById('ai-result-section').style.display = 'none';

      fetch('/user/ask-ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title, description: desc })
      })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        Loader.hide();
        askBtn.disabled = false;

        if (data.error) {
          showFlash(data.error, 'danger');
          return;
        }

        const resp = data.response || data;
        _lastAiResponse = resp.full_response || resp.answer || '';

        // Render markdown response
        const responseEl = document.getElementById('ai-response-content');
        if (responseEl) {
          responseEl.innerHTML = renderMarkdown(_lastAiResponse);
        }

        // Show retrieval context badge
        const ctxBadge = document.getElementById('ctx-badge');
        if (ctxBadge) {
          ctxBadge.style.display = resp.context_used ? 'inline-block' : 'none';
        }

        // Show result section
        document.getElementById('ai-result-section').style.display = 'block';
        document.getElementById('ai-result-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
      })
      .catch(function (err) {
        Loader.hide();
        askBtn.disabled = false;
        showFlash('Network error. Please try again.', 'danger');
        console.error(err);
      });
    });
  }

  // ── "It Works" button ───────────────────────────────────────────────────
  const worksBtn = document.getElementById('btn-works');
  if (worksBtn) {
    worksBtn.addEventListener('click', function () {
      document.getElementById('ai-result-section').style.display = 'none';
      document.getElementById('problem-title').value = '';
      document.getElementById('problem-description').value = '';
      showFlash('Great! Problem resolved. No ticket created.', 'success');
    });
  }

  // ── "Didn't Work" → Create Ticket ───────────────────────────────────────
  const didntWorkBtn = document.getElementById('btn-didnt-work');
  if (didntWorkBtn) {
    didntWorkBtn.addEventListener('click', function () {
      const title = document.getElementById('problem-title').value.trim();
      const desc  = document.getElementById('problem-description').value.trim();

      if (!title || !desc) {
        showFlash('Problem title and description are required to create a ticket.', 'warning');
        return;
      }

      Loader.show('Creating support ticket...');
      didntWorkBtn.disabled = true;

      fetch('/user/create-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title, description: desc, ai_solution: _lastAiResponse })
      })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        Loader.hide();
        didntWorkBtn.disabled = false;

        if (data.error) {
          showFlash(data.error, 'danger');
          return;
        }

        showFlash('Support ticket created. Our team will review it shortly.', 'success');
        document.getElementById('ai-result-section').style.display = 'none';
        document.getElementById('problem-title').value = '';
        document.getElementById('problem-description').value = '';

        // Reload tickets list
        setTimeout(function () { window.location.reload(); }, 1200);
      })
      .catch(function (err) {
        Loader.hide();
        didntWorkBtn.disabled = false;
        showFlash('Network error. Please try again.', 'danger');
        console.error(err);
      });
    });
  }
})();
