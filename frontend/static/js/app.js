/**
 * SupportPilot — Core Application JS
 * Flash message auto-dismiss, loader helpers, sidebar toggle
 */

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.sp-flash .alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.classList.remove('show');
      alert.classList.add('fade');
      setTimeout(function () { alert.remove(); }, 300);
    }, 5000);
  });

  // Sidebar mobile toggle
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sp-sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }
});

// Loader helpers
const Loader = {
  show: function (message) {
    const loader = document.getElementById('sp-loader');
    if (loader) {
      const label = loader.querySelector('.label');
      if (label) label.textContent = message || 'Loading...';
      loader.classList.add('active');
    }
  },
  hide: function () {
    const loader = document.getElementById('sp-loader');
    if (loader) loader.classList.remove('active');
  }
};

// Markdown-lite renderer for AI responses
function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^\*\*(.+)\*\*$/gm, '<strong>$1</strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^---$/gm, '<hr>')
    .replace(/^\d+\. (.+)$/gm, function(m, p1) { return `<li>${p1}</li>`; })
    .replace(/(<li>.*<\/li>\s*)+/g, function(m) { return `<ol>${m}</ol>`; })
    .replace(/^- (.+)$/gm, function(m, p1) { return `<li>${p1}</li>`; })
    .replace(/(<li>(?!.*<\/li>.*<\/li>).*<\/li>\s*)+/g, function(m) {
      if (!m.match(/<ol>/)) return `<ul>${m}</ul>`;
      return m;
    })
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

// Flash notification helper
function showFlash(message, type) {
  type = type || 'info';
  const container = document.querySelector('.sp-flash');
  if (!container) return;
  const div = document.createElement('div');
  div.className = `alert alert-${type} alert-dismissible fade show shadow-sm`;
  div.setAttribute('role', 'alert');
  div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.appendChild(div);
  setTimeout(function () {
    div.classList.remove('show');
    setTimeout(function () { div.remove(); }, 300);
  }, 5000);
}
