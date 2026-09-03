/**
 * CineVerse Modern OTT Streaming Client Runtime
 * Handles: Scroll effects, User menu toggle, Live search, Toast dismissal, Modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Navbar Glassmorphism on Scroll
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 2. User Profile Dropdown Toggle
  const avatarBtn = document.querySelector('.user-avatar-btn');
  const dropdownMenu = document.querySelector('.dropdown-menu');

  if (avatarBtn && dropdownMenu) {
    avatarBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdownMenu.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
      if (!dropdownMenu.contains(e.target) && !avatarBtn.contains(e.target)) {
        dropdownMenu.classList.remove('active');
      }
    });
  }

  // 3. Toast Auto-dismiss
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach((toast) => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  });

  // 4. Live Search Preview (Debounced)
  const searchInput = document.querySelector('.search-input');
  const searchDropdown = document.querySelector('.search-results-dropdown');

  if (searchInput && searchDropdown) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length < 2) {
        searchDropdown.style.display = 'none';
        searchDropdown.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/movies/api/search/?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            if (data.results && data.results.length > 0) {
              searchDropdown.innerHTML = data.results.map(item => `
                <a href="${item.url}" class="dropdown-item" style="padding: 0.75rem;">
                  <img src="${item.poster}" style="width: 36px; height: 50px; object-fit: cover; border-radius: 4px; margin-right: 0.75rem;">
                  <div>
                    <div style="font-weight: 600; color: #fff;">${item.title}</div>
                    <div style="font-size: 0.75rem; color: #8E95A5;">${item.type} • ${item.year}</div>
                  </div>
                </a>
              `).join('');
              searchDropdown.style.display = 'block';
            } else {
              searchDropdown.innerHTML = '<div style="padding: 1rem; color: #8E95A5; text-align: center; font-size: 0.85rem;">No streaming titles found</div>';
              searchDropdown.style.display = 'block';
            }
          })
          .catch(() => {
            searchDropdown.style.display = 'none';
          });
      }, 300);
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }
});
