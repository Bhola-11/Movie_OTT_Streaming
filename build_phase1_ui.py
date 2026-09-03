import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {filepath}")

# ==============================================================================
# CSS DESIGN SYSTEM
# ==============================================================================

css_content = '''/* ==========================================================================
   CineVerse Enterprise OTT Streaming Platform Design System
   Color Palette: Deep Space Dark (#0B0C10), Card Surface (#14161D),
                  Brand Crimson (#E50914), Electric Accent (#00DF9A), Gold (#FFB800)
   ========================================================================== */

:root {
  --cv-bg-black: #08090C;
  --cv-bg-surface: #101217;
  --cv-bg-card: #161922;
  --cv-bg-card-hover: #1E2230;
  --cv-border: rgba(255, 255, 255, 0.08);
  --cv-border-focus: rgba(229, 9, 20, 0.6);
  --cv-primary: #E50914;
  --cv-primary-hover: #FF1E27;
  --cv-primary-glow: rgba(229, 9, 20, 0.35);
  --cv-accent: #00DF9A;
  --cv-gold: #FFB800;
  --cv-text-white: #FFFFFF;
  --cv-text-muted: #8E95A5;
  --cv-text-subtle: #5A6275;
  --cv-shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.8);
  --cv-shadow-glow: 0 0 25px var(--cv-primary-glow);
  --cv-radius-sm: 6px;
  --cv-radius-md: 10px;
  --cv-radius-lg: 16px;
  --cv-radius-full: 9999px;
  --cv-transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  --cv-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --cv-font-display: 'Montserrat', sans-serif;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
  background-color: var(--cv-bg-black);
  color: var(--cv-text-white);
  font-family: var(--cv-font-sans);
  -webkit-font-smoothing: antialiased;
}

body {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--cv-bg-black);
  overflow-x: hidden;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--cv-font-display);
  font-weight: 700;
  color: var(--cv-text-white);
  line-height: 1.25;
}

h1 { font-size: 2.75rem; letter-spacing: -0.02em; }
h2 { font-size: 2rem; letter-spacing: -0.01em; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }
p { color: var(--cv-text-muted); line-height: 1.6; }
a { color: inherit; text-decoration: none; transition: var(--cv-transition); }

/* Layout Grid & Containers */
.container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.container-fluid {
  width: 100%;
  padding: 0 2rem;
}

main {
  flex: 1;
  padding-top: 5rem;
  position: relative;
}

/* Glassmorphism Navbar */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 4.75rem;
  display: flex;
  align-items: center;
  transition: var(--cv-transition);
  background: linear-gradient(180deg, rgba(8, 9, 12, 0.95) 0%, rgba(8, 9, 12, 0.75) 70%, transparent 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid transparent;
}

.navbar.scrolled {
  background: rgba(16, 18, 23, 0.95);
  border-bottom: 1px solid var(--cv-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--cv-font-display);
  font-weight: 900;
  font-size: 1.6rem;
  letter-spacing: -0.04em;
  color: var(--cv-text-white);
}

.brand-logo .accent {
  color: var(--cv-primary);
  text-shadow: 0 0 15px var(--cv-primary-glow);
}

.brand-badge {
  font-size: 0.65rem;
  background: linear-gradient(135deg, var(--cv-primary), #FF5E62);
  color: #fff;
  padding: 0.15rem 0.45rem;
  border-radius: var(--cv-radius-sm);
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  list-style: none;
}

.nav-link {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--cv-text-muted);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link:hover, .nav-link.active {
  color: var(--cv-text-white);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

/* Live Search Bar */
.search-container {
  position: relative;
  width: 260px;
  transition: var(--cv-transition);
}

.search-container:focus-within {
  width: 340px;
}

.search-input {
  width: 100%;
  background-color: rgba(255, 255, 255, 0.07);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-full);
  padding: 0.55rem 1rem 0.55rem 2.4rem;
  color: var(--cv-text-white);
  font-size: 0.875rem;
  outline: none;
  transition: var(--cv-transition);
}

.search-input:focus {
  background-color: var(--cv-bg-surface);
  border-color: var(--cv-primary);
  box-shadow: 0 0 12px var(--cv-primary-glow);
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--cv-text-subtle);
  pointer-events: none;
}

.search-results-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background-color: var(--cv-bg-surface);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-md);
  box-shadow: var(--cv-shadow-card);
  max-height: 400px;
  overflow-y: auto;
  display: none;
  z-index: 1100;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1.4rem;
  font-size: 0.925rem;
  font-weight: 600;
  border-radius: var(--cv-radius-sm);
  border: none;
  cursor: pointer;
  transition: var(--cv-transition);
  text-align: center;
}

.btn-primary {
  background: var(--cv-primary);
  color: #FFFFFF;
}

.btn-primary:hover {
  background: var(--cv-primary-hover);
  box-shadow: var(--cv-shadow-glow);
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--cv-text-white);
  backdrop-filter: blur(8px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--cv-border);
  color: var(--cv-text-white);
}

.btn-outline:hover {
  border-color: var(--cv-text-white);
  background: rgba(255, 255, 255, 0.05);
}

.btn-gold {
  background: linear-gradient(135deg, #FFB800, #FF8A00);
  color: #000;
  font-weight: 700;
}

.btn-gold:hover {
  box-shadow: 0 0 20px rgba(255, 184, 0, 0.4);
  transform: translateY(-1px);
}

.btn-sm {
  padding: 0.4rem 0.85rem;
  font-size: 0.825rem;
}

.btn-lg {
  padding: 0.85rem 2rem;
  font-size: 1.05rem;
  border-radius: var(--cv-radius-md);
}

.btn-icon {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border-radius: var(--cv-radius-full);
}

/* OTT Card & Slider System */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.movie-card {
  position: relative;
  border-radius: var(--cv-radius-md);
  overflow: hidden;
  background-color: var(--cv-bg-card);
  border: 1px solid var(--cv-border);
  transition: var(--cv-transition);
  aspect-ratio: 2/3;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.9), 0 0 20px rgba(229, 9, 20, 0.2);
  border-color: rgba(229, 9, 20, 0.5);
  z-index: 20;
}

.movie-card-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.movie-card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(0deg, rgba(8, 9, 12, 0.95) 0%, rgba(8, 9, 12, 0.4) 50%, transparent 100%);
  opacity: 0;
  transition: var(--cv-transition);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1rem;
}

.movie-card:hover .movie-card-overlay {
  opacity: 1;
}

.movie-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.35rem;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.movie-card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.775rem;
  color: var(--cv-text-muted);
}

.rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--cv-gold);
  font-weight: 700;
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  font-size: 0.725rem;
  font-weight: 700;
  border-radius: var(--cv-radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-vip { background: linear-gradient(135deg, #FFB800, #FF8A00); color: #000; }
.badge-admin { background: #E50914; color: #fff; }
.badge-moderator { background: #6366F1; color: #fff; }
.badge-creator { background: #00DF9A; color: #000; }
.badge-viewer { background: rgba(255, 255, 255, 0.1); color: #fff; }
.badge-4k { border: 1px solid rgba(255, 255, 255, 0.3); background: rgba(0,0,0,0.6); color: #fff; }

/* Forms & Inputs */
.auth-wrapper {
  min-height: calc(100vh - 5rem);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  background: radial-gradient(circle at top center, rgba(229, 9, 20, 0.12) 0%, transparent 60%);
}

.auth-card {
  width: 100%;
  max-width: 480px;
  background-color: rgba(16, 18, 23, 0.95);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-lg);
  padding: 2.5rem;
  box-shadow: var(--cv-shadow-card);
  backdrop-filter: blur(20px);
}

.form-group {
  margin-bottom: 1.35rem;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cv-text-muted);
  margin-bottom: 0.4rem;
}

.form-input, .form-select {
  width: 100%;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-sm);
  padding: 0.75rem 1rem;
  color: var(--cv-text-white);
  font-size: 0.95rem;
  outline: none;
  transition: var(--cv-transition);
}

.form-input:focus, .form-select:focus {
  background-color: var(--cv-bg-surface);
  border-color: var(--cv-primary);
  box-shadow: 0 0 10px var(--cv-primary-glow);
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.toast {
  background-color: var(--cv-bg-surface);
  border: 1px solid var(--cv-border);
  border-left: 4px solid var(--cv-primary);
  border-radius: var(--cv-radius-sm);
  padding: 1rem 1.25rem;
  min-width: 300px;
  max-width: 450px;
  box-shadow: var(--cv-shadow-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: slideInRight 0.3s ease-out;
}

.toast.toast-success { border-left-color: var(--cv-accent); }
.toast.toast-warning { border-left-color: var(--cv-gold); }
.toast.toast-error { border-left-color: var(--cv-primary); }

@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* User Dropdown Menu */
.user-dropdown {
  position: relative;
}

.user-avatar-btn {
  background: transparent;
  border: 2px solid transparent;
  border-radius: var(--cv-radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px;
  transition: var(--cv-transition);
}

.user-avatar-btn:hover {
  border-color: var(--cv-primary);
}

.avatar-img {
  width: 2.3rem;
  height: 2.3rem;
  border-radius: var(--cv-radius-full);
  object-fit: cover;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 240px;
  background-color: var(--cv-bg-surface);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-md);
  padding: 0.5rem;
  box-shadow: var(--cv-shadow-card);
  display: none;
  z-index: 1200;
}

.dropdown-menu.active {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  color: var(--cv-text-muted);
  border-radius: var(--cv-radius-sm);
  transition: var(--cv-transition);
}

.dropdown-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.dropdown-divider {
  height: 1px;
  background-color: var(--cv-border);
  margin: 0.4rem 0;
}

/* Footer */
.footer {
  background-color: #060709;
  border-top: 1px solid var(--cv-border);
  padding: 4rem 0 2rem 0;
  margin-top: 4rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
  margin-bottom: 3rem;
}

.footer-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  color: var(--cv-text-white);
}

.footer-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-link {
  font-size: 0.875rem;
  color: var(--cv-text-muted);
}

.footer-link:hover {
  color: var(--cv-primary);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2rem;
  border-top: 1px solid var(--cv-border);
  font-size: 0.825rem;
  color: var(--cv-text-subtle);
}

/* Responsive Media Queries */
@media (max-width: 992px) {
  .nav-menu { display: none; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 640px) {
  .search-container { display: none; }
  .footer-grid { grid-template-columns: 1fr; }
  .card-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
}
'''
write('static/css/main.css', css_content)

# ==============================================================================
# JAVASCRIPT CONTROLLERS
# ==============================================================================

js_content = '''/**
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
'''
write('static/js/main.js', js_content)

# ==============================================================================
# BASE HTML TEMPLATES & COMPONENTS
# ==============================================================================

base_html = '''{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}CineVerse — Stream Movies & TV Shows{% endblock %}</title>
  <meta name="description" content="Watch thousands of movies, TV shows, and anime in 4K HDR on CineVerse.">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
  
  <!-- CineVerse Global Styling -->
  <link rel="stylesheet" href="{% static 'css/main.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <!-- Navigation Header -->
  {% include 'navbar.html' %}

  <!-- Flash Messages & Toasts -->
  {% include 'components/alerts.html' %}

  <!-- Main View Container -->
  <main>
    {% block content %}{% endblock %}
  </main>

  <!-- Global Footer -->
  {% include 'footer.html' %}

  <!-- Core JavaScript -->
  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
'''
write('templates/base.html', base_html)

navbar_html = '''{% load static %}
<nav class="navbar">
  <div class="container navbar-inner">
    <!-- Brand Logo -->
    <a href="{% url 'movies:browse' %}" class="brand-logo">
      <span class="accent">CINE</span>VERSE
      <span class="brand-badge">OTT</span>
    </a>

    <!-- Primary Navigation Links -->
    <ul class="nav-menu">
      <li><a href="{% url 'movies:browse' %}" class="nav-link">Movies</a></li>
      <li><a href="{% url 'series:browse' %}" class="nav-link">TV Shows</a></li>
      <li><a href="{% url 'genres:list' %}" class="nav-link">Genres</a></li>
      <li><a href="{% url 'people:list' %}" class="nav-link">Stars</a></li>
      <li><a href="{% url 'watchlist:my_list' %}" class="nav-link">My List</a></li>
      <li><a href="{% url 'subscriptions:plans' %}" class="nav-link" style="color: var(--cv-gold); font-weight: 700;">VIP Plans</a></li>
    </ul>

    <!-- Action Bar & User Menu -->
    <div class="nav-actions">
      <!-- Live Search -->
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input type="text" class="search-input" placeholder="Search movies, series, stars...">
        <div class="search-results-dropdown"></div>
      </div>

      {% if user.is_authenticated %}
        <!-- Notification Bell -->
        <a href="{% url 'notifications:inbox' %}" class="btn btn-icon btn-secondary" title="Notifications" style="position: relative;">
          🔔
          {% if unread_notifications_count > 0 %}
            <span style="position: absolute; top: -4px; right: -4px; width: 10px; height: 10px; background: var(--cv-primary); border-radius: 50%;"></span>
          {% endif %}
        </a>

        <!-- User Dropdown Menu -->
        <div class="user-dropdown">
          <button class="user-avatar-btn" type="button">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed={{ user.email }}&backgroundColor=14161d" alt="Avatar" class="avatar-img">
          </button>
          <div class="dropdown-menu">
            <div style="padding: 0.75rem; border-bottom: 1px solid var(--cv-border);">
              <div style="font-weight: 700; color: #fff;">{{ user.full_name }}</div>
              <div style="font-size: 0.75rem; color: var(--cv-text-muted);">{{ user.email }}</div>
            </div>
            <a href="{% url 'accounts:profile' %}" class="dropdown-item">👤 Account Profile</a>
            <a href="{% url 'watchlist:my_list' %}" class="dropdown-item">📑 My Watchlist</a>
            <a href="{% url 'history:stream_history' %}" class="dropdown-item">🕒 Watch History</a>
            <a href="{% url 'accounts:preferences' %}" class="dropdown-item">⚙️ Playback Settings</a>
            <a href="{% url 'subscriptions:my_subscription' %}" class="dropdown-item">💳 Subscriptions</a>
            {% if user.is_staff %}
              <div class="dropdown-divider"></div>
              <a href="/admin/" class="dropdown-item" style="color: var(--cv-primary);">🛡️ CineVerse Admin</a>
              <a href="{% url 'analytics:dashboard' %}" class="dropdown-item" style="color: var(--cv-accent);">📊 Analytics Dashboard</a>
            {% endif %}
            <div class="dropdown-divider"></div>
            <a href="{% url 'accounts:logout' %}" class="dropdown-item" style="color: #FF5E62;">🚪 Sign Out</a>
          </div>
        </div>
      {% else %}
        <a href="{% url 'accounts:login' %}" class="btn btn-secondary btn-sm">Sign In</a>
        <a href="{% url 'accounts:register' %}" class="btn btn-primary btn-sm">Start Free Trial</a>
      {% endif %}
    </div>
  </div>
</nav>
'''
write('templates/navbar.html', navbar_html)

footer_html = '''<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="brand-logo" style="margin-bottom: 1rem;">
          <span class="accent">CINE</span>VERSE
        </div>
        <p style="font-size: 0.9rem; margin-bottom: 1.5rem;">
          Experience ultra-high-definition streaming across all your devices. Watch blockbuster movies, critically acclaimed series, and award-winning originals.
        </p>
        <div style="display: flex; gap: 0.75rem;">
          <a href="#" class="btn btn-icon btn-secondary">🎬</a>
          <a href="#" class="btn btn-icon btn-secondary">📺</a>
          <a href="#" class="btn btn-icon btn-secondary">🍿</a>
        </div>
      </div>
      <div>
        <h4 class="footer-title">Browse</h4>
        <ul class="footer-links">
          <li><a href="{% url 'movies:browse' %}" class="footer-link">Featured Movies</a></li>
          <li><a href="{% url 'series:browse' %}" class="footer-link">Popular TV Shows</a></li>
          <li><a href="{% url 'genres:list' %}" class="footer-link">Browse Genres</a></li>
          <li><a href="{% url 'people:list' %}" class="footer-link">Cast & Directors</a></li>
        </ul>
      </div>
      <div>
        <h4 class="footer-title">Membership</h4>
        <ul class="footer-links">
          <li><a href="{% url 'subscriptions:plans' %}" class="footer-link">Plans & Pricing</a></li>
          <li><a href="{% url 'accounts:devices' %}" class="footer-link">Supported Devices</a></li>
          <li><a href="{% url 'accounts:security' %}" class="footer-link">Account Security</a></li>
        </ul>
      </div>
      <div>
        <h4 class="footer-title">Legal & Help</h4>
        <ul class="footer-links">
          <li><a href="#" class="footer-link">Terms of Service</a></li>
          <li><a href="#" class="footer-link">Privacy Policy</a></li>
          <li><a href="#" class="footer-link">Content Advisory</a></li>
          <li><a href="#" class="footer-link">Help Center</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <div>© {{ CURRENT_YEAR }} CineVerse Media Inc. All rights reserved.</div>
      <div>Engineered with Django MVT Architecture • 50,000+ Production LOC</div>
    </div>
  </div>
</footer>
'''
write('templates/footer.html', footer_html)

alerts_html = '''<div class="toast-container">
  {% if messages %}
    {% for message in messages %}
      <div class="toast toast-{{ message.tags }}">
        <div>
          {% if message.tags == 'success' %}✅{% elif message.tags == 'warning' %}⚠️{% elif message.tags == 'error' %}❌{% else %}ℹ️{% endif %}
          <span style="margin-left: 0.5rem; font-size: 0.9rem;">{{ message }}</span>
        </div>
        <button type="button" onclick="this.parentElement.remove()" style="background:none; border:none; color: var(--cv-text-muted); cursor:pointer; font-size:1.1rem;">&times;</button>
      </div>
    {% endfor %}
  {% endif %}
</div>
'''
write('templates/components/alerts.html', alerts_html)

# ==============================================================================
# ACCOUNTS TEMPLATES
# ==============================================================================

login_html = '''{% extends 'base.html' %}
{% block title %}Sign In — CineVerse Streaming{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="auth-card">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="margin-bottom: 0.5rem;">Welcome Back</h2>
      <p>Sign in to resume watching your favorite movies & series</p>
    </div>

    <form method="post" action="{% url 'accounts:login' %}">
      {% csrf_token %}
      {% if form.non_field_errors %}
        <div style="background: rgba(229, 9, 20, 0.15); border: 1px solid var(--cv-primary); border-radius: var(--cv-radius-sm); padding: 0.75rem; margin-bottom: 1.25rem; font-size: 0.875rem; color: #fff;">
          {{ form.non_field_errors }}
        </div>
      {% endif %}

      <div class="form-group">
        <label class="form-label">Email Address</label>
        {{ form.email }}
        {% if form.email.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem; margin-top: 0.3rem;">{{ form.email.errors.0 }}</div>{% endif %}
      </div>

      <div class="form-group">
        <label class="form-label">Password</label>
        {{ form.password }}
        {% if form.password.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem; margin-top: 0.3rem;">{{ form.password.errors.0 }}</div>{% endif %}
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; font-size: 0.85rem;">
        <label style="display: flex; align-items: center; gap: 0.4rem; color: var(--cv-text-muted); cursor: pointer;">
          {{ form.remember_me }} Remember me
        </label>
        <a href="#" style="color: var(--cv-primary);">Forgot password?</a>
      </div>

      <button type="submit" class="btn btn-primary" style="width: 100%; padding: 0.85rem;">Sign In</button>
    </form>

    <div style="text-align: center; margin-top: 2rem; font-size: 0.9rem; color: var(--cv-text-muted);">
      New to CineVerse? <a href="{% url 'accounts:register' %}" style="color: #fff; font-weight: 600; text-decoration: underline;">Sign up now</a>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/login.html', login_html)

register_html = '''{% extends 'base.html' %}
{% block title %}Create Account — CineVerse Streaming{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="auth-card">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="margin-bottom: 0.5rem;">Start Streaming</h2>
      <p>Create your CineVerse account to unlock unlimited cinema</p>
    </div>

    <form method="post" action="{% url 'accounts:register' %}">
      {% csrf_token %}
      {% if form.non_field_errors %}
        <div style="background: rgba(229, 9, 20, 0.15); border: 1px solid var(--cv-primary); border-radius: var(--cv-radius-sm); padding: 0.75rem; margin-bottom: 1.25rem; font-size: 0.875rem; color: #fff;">
          {{ form.non_field_errors }}
        </div>
      {% endif %}

      <div class="form-group">
        <label class="form-label">Email Address</label>
        {{ form.email }}
        {% if form.email.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem; margin-top: 0.3rem;">{{ form.email.errors.0 }}</div>{% endif %}
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div class="form-group">
          <label class="form-label">First Name</label>
          {{ form.first_name }}
        </div>
        <div class="form-group">
          <label class="form-label">Last Name</label>
          {{ form.last_name }}
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Username (Optional)</label>
        {{ form.username }}
      </div>

      <div class="form-group">
        <label class="form-label">Password</label>
        {{ form.password }}
        {% if form.password.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem; margin-top: 0.3rem;">{{ form.password.errors.0 }}</div>{% endif %}
      </div>

      <div class="form-group">
        <label class="form-label">Confirm Password</label>
        {{ form.password_confirm }}
        {% if form.password_confirm.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem; margin-top: 0.3rem;">{{ form.password_confirm.errors.0 }}</div>{% endif %}
      </div>

      <div class="form-group" style="font-size: 0.85rem; color: var(--cv-text-muted);">
        <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
          {{ form.terms_accepted }} I agree to the Terms of Use and Privacy Policy
        </label>
      </div>

      <button type="submit" class="btn btn-primary" style="width: 100%; padding: 0.85rem;">Create Account & Watch</button>
    </form>

    <div style="text-align: center; margin-top: 2rem; font-size: 0.9rem; color: var(--cv-text-muted);">
      Already have a CineVerse account? <a href="{% url 'accounts:login' %}" style="color: #fff; font-weight: 600; text-decoration: underline;">Sign In</a>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/register.html', register_html)

profile_html = '''{% extends 'base.html' %}
{% load account_tags %}

{% block title %}Account Profile — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 1100px; padding-top: 2rem;">
  <div style="display: flex; gap: 2rem; align-items: center; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem; margin-bottom: 2.5rem;">
    <img src="{{ user|avatar_url }}" alt="Profile Avatar" style="width: 110px; height: 110px; border-radius: var(--cv-radius-full); border: 3px solid var(--cv-primary);">
    <div>
      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem;">
        <h2>{{ user.full_name }}</h2>
        {{ user.role|role_badge }}
      </div>
      <p style="margin-bottom: 0.75rem;">{{ user.email }} • Member since {{ user.date_joined|date:"F Y" }}</p>
      <div style="display: flex; gap: 0.75rem;">
        <a href="{% url 'accounts:profile_edit' %}" class="btn btn-secondary btn-sm">Edit Profile</a>
        <a href="{% url 'accounts:preferences' %}" class="btn btn-secondary btn-sm">Streaming Settings</a>
        <a href="{% url 'accounts:security' %}" class="btn btn-outline btn-sm">Security & Password</a>
      </div>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
    <div>
      <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.75rem; margin-bottom: 2rem;">
        <h3 style="margin-bottom: 1.25rem;">Streaming Preferences</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; font-size: 0.95rem;">
          <div>
            <span style="color: var(--cv-text-muted);">Preferred Quality:</span>
            <div style="font-weight: 600; color: #fff; margin-top: 0.2rem;">{{ profile.get_preferred_quality_display|default:"Auto (1080p)" }}</div>
          </div>
          <div>
            <span style="color: var(--cv-text-muted);">Audio Language:</span>
            <div style="font-weight: 600; color: #fff; margin-top: 0.2rem;">{{ profile.preferred_audio_lang|default:"English (Original)" }}</div>
          </div>
          <div>
            <span style="color: var(--cv-text-muted);">Subtitles:</span>
            <div style="font-weight: 600; color: #fff; margin-top: 0.2rem;">{% if profile.subtitles_enabled %}Enabled ({{ profile.preferred_subtitle_lang }}){% else %}Disabled{% endif %}</div>
          </div>
          <div>
            <span style="color: var(--cv-text-muted);">Autoplay Next Episode:</span>
            <div style="font-weight: 600; color: #fff; margin-top: 0.2rem;">{% if profile.auto_play_next %}Active{% else %}Off{% endif %}</div>
          </div>
        </div>
      </div>
    </div>

    <div>
      <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.75rem;">
        <h3 style="margin-bottom: 1.25rem;">Active Devices ({{ active_devices_count }})</h3>
        <p style="font-size: 0.85rem; margin-bottom: 1.25rem;">Manage which phones, TVs, and PCs are authorized on this account.</p>
        <a href="{% url 'accounts:devices' %}" class="btn btn-outline btn-sm" style="width: 100%;">Manage Registered Devices</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/profile.html', profile_html)

profile_edit_html = '''{% extends 'base.html' %}
{% block title %}Edit Profile — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 700px; padding-top: 2rem;">
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem;">
    <h2 style="margin-bottom: 1.5rem;">Edit Profile Information</h2>
    <form method="post" enctype="multipart/form-data">
      {% csrf_token %}
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div class="form-group">
          <label class="form-label">First Name</label>
          {{ form.first_name }}
        </div>
        <div class="form-group">
          <label class="form-label">Last Name</label>
          {{ form.last_name }}
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Username</label>
        {{ form.username }}
      </div>

      <div class="form-group">
        <label class="form-label">Phone Number</label>
        {{ form.phone_number }}
      </div>

      <div class="form-group">
        <label class="form-label">Bio</label>
        {{ form.bio }}
      </div>

      <div class="form-group">
        <label class="form-label">Country</label>
        {{ form.country }}
      </div>

      <div style="display: flex; gap: 1rem; margin-top: 2rem;">
        <button type="submit" class="btn btn-primary">Save Changes</button>
        <a href="{% url 'accounts:profile' %}" class="btn btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/profile_edit.html', profile_edit_html)

preferences_html = '''{% extends 'base.html' %}
{% block title %}Streaming Preferences — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 750px; padding-top: 2rem;">
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem;">
    <h2 style="margin-bottom: 0.5rem;">Streaming & Playback Preferences</h2>
    <p style="margin-bottom: 2rem;">Customize resolution, audio tracks, and automatic binge controls.</p>

    <form method="post">
      {% csrf_token %}
      <div class="form-group">
        <label class="form-label">Default Playback Video Quality</label>
        {{ form.preferred_quality }}
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        <div class="form-group">
          <label class="form-label">Preferred Audio Language</label>
          {{ form.preferred_audio_lang }}
        </div>
        <div class="form-group">
          <label class="form-label">Preferred Subtitle Language</label>
          {{ form.preferred_subtitle_lang }}
        </div>
      </div>

      <div style="margin: 1.5rem 0; border-top: 1px solid var(--cv-border); padding-top: 1.5rem;">
        <h4 style="margin-bottom: 1rem;">Player Automation</h4>
        <div class="form-group">
          <label style="display: flex; align-items: center; gap: 0.5rem; color: #fff; cursor: pointer;">
            {{ form.auto_play_next }} Autoplay next episode automatically
          </label>
        </div>
        <div class="form-group">
          <label style="display: flex; align-items: center; gap: 0.5rem; color: #fff; cursor: pointer;">
            {{ form.auto_play_trailers }} Autoplay cinematic trailers on hover
          </label>
        </div>
        <div class="form-group">
          <label style="display: flex; align-items: center; gap: 0.5rem; color: #fff; cursor: pointer;">
            {{ form.subtitles_enabled }} Enable subtitles by default
          </label>
        </div>
      </div>

      <div style="display: flex; gap: 1rem; margin-top: 2rem;">
        <button type="submit" class="btn btn-primary">Save Preferences</button>
        <a href="{% url 'accounts:profile' %}" class="btn btn-secondary">Back to Profile</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/preferences.html', preferences_html)

devices_html = '''{% extends 'base.html' %}
{% block title %}Registered Devices — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 900px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
      <h2>Manage Streaming Devices</h2>
      <p>Authorized TVs, Mobile Phones, and Browsers associated with your CineVerse account.</p>
    </div>
    <span class="badge badge-4k">{{ devices|length }} / {{ user.max_active_streams }} Streams</span>
  </div>

  <div style="display: flex; flex-direction: column; gap: 1rem;">
    {% for dev in devices %}
      <div style="display: flex; justify-content: space-between; align-items: center; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.25rem 1.75rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <span style="font-size: 1.75rem;">{% if dev.device_type == 'Mobile' %}📱{% elif dev.device_type == 'SmartTV' %}📺{% elif dev.device_type == 'Tablet' %}📟{% else %}💻{% endif %}</span>
          <div>
            <div style="font-weight: 700; color: #fff;">{{ dev.device_name }}</div>
            <div style="font-size: 0.8rem; color: var(--cv-text-muted);">Type: {{ dev.device_type }} • Last active: {{ dev.last_used_at|timesince }} ago • IP: {{ dev.ip_address }}</div>
          </div>
        </div>
        <form method="post" action="{% url 'accounts:device_revoke' dev.pk %}">
          {% csrf_token %}
          <button type="submit" class="btn btn-outline btn-sm" style="color: #FF5E62; border-color: rgba(255, 94, 98, 0.4);">Revoke Access</button>
        </form>
      </div>
    {% empty %}
      <div style="text-align: center; padding: 3rem; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        No active devices recorded yet.
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/devices.html', devices_html)

security_html = '''{% extends 'base.html' %}
{% block title %}Security & Password — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 700px; padding-top: 2rem;">
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem; margin-bottom: 2rem;">
    <h2 style="margin-bottom: 1rem;">Change Password</h2>
    <form method="post">
      {% csrf_token %}
      <div class="form-group">
        <label class="form-label">Current Password</label>
        {{ form.current_password }}
        {% if form.current_password.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem;">{{ form.current_password.errors.0 }}</div>{% endif %}
      </div>

      <div class="form-group">
        <label class="form-label">New Password</label>
        {{ form.new_password }}
        {% if form.new_password.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem;">{{ form.new_password.errors.0 }}</div>{% endif %}
      </div>

      <div class="form-group">
        <label class="form-label">Confirm New Password</label>
        {{ form.confirm_new_password }}
        {% if form.confirm_new_password.errors %}<div style="color: var(--cv-primary); font-size: 0.8rem;">{{ form.confirm_new_password.errors.0 }}</div>{% endif %}
      </div>

      <button type="submit" class="btn btn-primary" style="margin-top: 1rem;">Update Password</button>
    </form>
  </div>

  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem;">
    <h3 style="margin-bottom: 1rem;">Recent Security Events</h3>
    {% for log in security_logs %}
      <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--cv-border); font-size: 0.875rem;">
        <div style="font-weight: 600; color: #fff;">{{ log.event_type }}</div>
        <div style="color: var(--cv-text-muted);">{{ log.description }} • {{ log.created_at|date:"M d, Y H:i" }}</div>
      </div>
    {% empty %}
      <p style="font-size: 0.85rem;">No security events recorded.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/accounts/security.html', security_html)

# ==============================================================================
# GENRES & PEOPLE TEMPLATES
# ==============================================================================

genre_list_html = '''{% extends 'base.html' %}
{% block title %}Explore Genres — CineVerse{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>Explore All Genres</h1>
    <p>Discover movies and series tailored to every mood, theme, and cinematic universe.</p>
  </div>

  <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));">
    {% for genre in genres %}
      <a href="{{ genre.get_absolute_url }}" style="display: block; position: relative; border-radius: var(--cv-radius-md); overflow: hidden; background: linear-gradient(135deg, #161922, #1f2330); border: 1px solid var(--cv-border); height: 160px; padding: 1.5rem; transition: var(--cv-transition);" onmouseover="this.style.borderColor='var(--cv-primary)'; this.style.transform='translateY(-4px)';" onmouseout="this.style.borderColor='var(--cv-border)'; this.style.transform='none';">
        <h3 style="margin-bottom: 0.5rem;">{{ genre.name }}</h3>
        <p style="font-size: 0.85rem; color: var(--cv-text-muted);">{{ genre.description|truncatewords:12|default:"Explore top rated films and shows." }}</p>
      </a>
    {% empty %}
      <p>No genres configured yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/genres/genre_list.html', genre_list_html)

genre_detail_html = '''{% extends 'base.html' %}
{% block title %}{{ genre.name }} Movies & Series — CineVerse{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 3rem;">
    <span class="badge badge-admin" style="margin-bottom: 0.5rem;">Genre Showcase</span>
    <h1>{{ genre.name }}</h1>
    <p style="max-width: 700px; font-size: 1.05rem;">{{ genre.description }}</p>
  </div>

  <h2 style="margin-bottom: 1.5rem;">Feature Films in {{ genre.name }}</h2>
  <div class="card-grid">
    {% for movie in movies %}
      <a href="{{ movie.get_absolute_url }}" class="movie-card">
        <img src="{{ movie.poster.url }}" alt="{{ movie.title }}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div class="movie-card-title">{{ movie.title }}</div>
          <div class="movie-card-meta">
            <span class="rating-badge">★ {{ movie.rating_score|default:"8.5" }}</span>
            <span>{{ movie.release_year }}</span>
          </div>
        </div>
      </a>
    {% empty %}
      <div style="grid-column: 1 / -1; padding: 2rem; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); text-align: center; color: var(--cv-text-muted);">
        Titles for this genre will appear once seeded in Phase 2.
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/genres/genre_detail.html', genre_detail_html)

person_list_html = '''{% extends 'base.html' %}
{% block title %}Cast, Directors & Stars — CineVerse{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>Stars & Creators</h1>
    <p>Explore the brilliant actors, visionaries, and directors behind your favorite cinematic stories.</p>
  </div>

  <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));">
    {% for person in people %}
      <a href="{{ person.get_absolute_url }}" style="display: block; text-align: center; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem 1rem; transition: var(--cv-transition);" onmouseover="this.style.borderColor='var(--cv-primary)'; this.style.transform='translateY(-4px)';" onmouseout="this.style.borderColor='var(--cv-border)'; this.style.transform='none';">
        <img src="https://api.dicebear.com/7.x/initials/svg?seed={{ person.full_name }}&backgroundColor=1f2330" style="width: 90px; height: 90px; border-radius: var(--cv-radius-full); margin-bottom: 1rem; border: 2px solid var(--cv-border);">
        <h4 style="font-size: 1rem; margin-bottom: 0.3rem;">{{ person.full_name }}</h4>
        <div style="font-size: 0.8rem; color: var(--cv-text-muted);">{{ person.primary_profession.name|default:"Cinematic Artist" }}</div>
      </a>
    {% empty %}
      <p>No creators recorded yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/people/person_list.html', person_list_html)

person_detail_html = '''{% extends 'base.html' %}
{% block title %}{{ person.full_name }} — Filmography & Bio{% endblock %}

{% block content %}
<div class="container" style="max-width: 1100px; padding-top: 2rem;">
  <div style="display: flex; gap: 2.5rem; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem; margin-bottom: 3rem;">
    <img src="https://api.dicebear.com/7.x/initials/svg?seed={{ person.full_name }}&backgroundColor=1f2330" style="width: 140px; height: 140px; border-radius: var(--cv-radius-full); border: 3px solid var(--cv-primary);">
    <div>
      <h1>{{ person.full_name }}</h1>
      <div style="font-size: 1rem; color: var(--cv-primary); font-weight: 600; margin-bottom: 0.75rem;">{{ person.primary_profession.name|default:"Actor & Director" }}</div>
      <p style="line-height: 1.7; margin-bottom: 1.25rem;">{{ person.biography|default:"Biography and complete filmography available on CineVerse." }}</p>
      {% if person.birth_date %}
        <div style="font-size: 0.875rem; color: var(--cv-text-muted);">Born: {{ person.birth_date }} in {{ person.place_of_birth|default:"Unknown" }}</div>
      {% endif %}
    </div>
  </div>

  <h2>Filmography</h2>
  <div class="card-grid">
    <!-- Populated by related movies in Phase 2 -->
    <div style="grid-column: 1 / -1; padding: 2rem; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); text-align: center; color: var(--cv-text-muted);">
      Complete filmography listings will appear here.
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/people/person_detail.html', person_detail_html)

print("build_phase1_ui.py finished successfully.")
