function searchProjects() {
  const searchQuery = (document.getElementById('search-input').value || '').toLowerCase().trim();
  const cards = document.querySelectorAll('.project-card');

  cards.forEach(card => {
    const titleEl = card.querySelector('.project-title');
    const statusEl = card.querySelector('.status');
    const categoryEl = card.querySelector('.project-category');

    const title = titleEl ? titleEl.textContent.toLowerCase() : '';
    const status = statusEl ? statusEl.textContent.toLowerCase() : '';
    const category = categoryEl ? categoryEl.textContent.toLowerCase() : '';

    if (!searchQuery || title.includes(searchQuery) || status.includes(searchQuery) || category.includes(searchQuery)) {
      card.classList.remove('is-hidden');
    } else {
      card.classList.add('is-hidden');
    }
  });
}

// wire up input and button
const searchInput = document.getElementById('search-input');
if (searchInput) {
  searchInput.addEventListener('input', searchProjects);
}
const searchButton = document.getElementById('search-button');
if (searchButton) {
  searchButton.addEventListener('click', searchProjects);
}