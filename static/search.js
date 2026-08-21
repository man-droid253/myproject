let _searchTimer = null;
const DEBOUNCE_MS = 250;

function escapeHtml(text) {
  return text.replace(/[&"'<>]/g, (c) => ({
    '&': '&amp;', '"': '&quot;', "'": '&#39;', '<': '&lt;', '>': '&gt;'
  }[c]));
}

function highlightElement(el, query) {
  if (!el) return;
  const original = el.dataset.original || el.textContent;
  el.dataset.original = original;
  if (!query) {
    el.innerHTML = escapeHtml(original);
    return;
  }
  try {
    const re = new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
    el.innerHTML = escapeHtml(original).replace(re, '<mark>$1</mark>');
  } catch (e) {
    el.innerHTML = escapeHtml(original);
  }
}

function searchProjects() {
  const raw = (document.getElementById('search-input').value || '').trim();
  const searchQuery = raw.toLowerCase();
  const cards = document.querySelectorAll('.project-card');

  cards.forEach(card => {
    const titleEl = card.querySelector('.project-title');
    const statusEl = card.querySelector('.status');
    const categoryEl = card.querySelector('.project-category');

    const title = titleEl ? (titleEl.dataset.original || titleEl.textContent).toLowerCase() : '';
    const status = statusEl ? (statusEl.dataset.original || statusEl.textContent).toLowerCase() : '';
    const category = categoryEl ? (categoryEl.dataset.original || categoryEl.textContent).toLowerCase() : '';

    const matched = !searchQuery || title.includes(searchQuery) || status.includes(searchQuery) || category.includes(searchQuery);

    if (matched) {
      card.classList.remove('is-hidden');
    } else {
      card.classList.add('is-hidden');
    }

    // highlight matches within visible cards
    highlightElement(titleEl, searchQuery);
    highlightElement(statusEl, searchQuery);
    highlightElement(categoryEl, searchQuery);
  });
}

// wire up input, button, clear, and keyboard shortcuts with debounce
const searchInput = document.getElementById('search-input');
if (searchInput) {
  searchInput.addEventListener('input', () => {
    if (_searchTimer) clearTimeout(_searchTimer);
    _searchTimer = setTimeout(searchProjects, DEBOUNCE_MS);
  });

  // Enter triggers server-side search (navigate to /projects?q=...)
  searchInput.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter') {
      ev.preventDefault();
      const q = encodeURIComponent(searchInput.value.trim());
      window.location.href = '/projects' + (q ? ('?q=' + q) : '');
    }

    // keyboard shortcut: press '/' to focus (when not typing)
    // handled globally below
  });
}

const searchButton = document.getElementById('search-button');
if (searchButton) {
  searchButton.addEventListener('click', () => {
    const q = encodeURIComponent((document.getElementById('search-input').value || '').trim());
    const status = encodeURIComponent((document.getElementById('filter-status')?.value || '').trim());
    let url = '/projects';
    const params = [];
    if (q) params.push('q=' + q);
    if (status) params.push('status=' + status);
    if (params.length) url += '?' + params.join('&');
    window.location.href = url;
  });
}

const clearButton = document.getElementById('search-clear');
if (clearButton) {
  clearButton.addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    const fs = document.getElementById('filter-status');
    if (fs) fs.value = '';
    searchProjects();
  });
}

const statusSelect = document.getElementById('filter-status');
if (statusSelect) {
  statusSelect.addEventListener('change', () => {
    // apply client-side filter immediately
    searchProjects();
  });
}

// global shortcut: focus search when pressing '/'
document.addEventListener('keydown', (ev) => {
  // don't hijack when the user is typing in an input or textarea
  const active = document.activeElement;
  if (ev.key === '/' && active && (active.tagName !== 'INPUT' && active.tagName !== 'TEXTAREA')) {
    ev.preventDefault();
    const input = document.getElementById('search-input');
    if (input) input.focus();
  }
});