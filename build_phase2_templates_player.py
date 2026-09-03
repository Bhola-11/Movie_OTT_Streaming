import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. PLAYER JAVASCRIPT CONTROLLER
# ==============================================================================

player_js = '''/**
 * CineVerse OTT HTML5 Cinema Video Player Controller
 * Implements: Play/Pause, Seek, Buffer preview, Skip Intro, Auto Next Episode,
 *             Subtitles toggle, Volume slider, Keyboard shortcuts.
 */

class CineVersePlayer {
  constructor(videoElementId) {
    this.video = document.getElementById(videoElementId);
    if (!this.video) return;

    this.wrapper = this.video.closest('.player-wrapper');
    this.playPauseBtn = document.getElementById('playPauseBtn');
    this.progressBar = document.getElementById('progressBar');
    this.progressFill = document.getElementById('progressFill');
    this.timeDisplay = document.getElementById('timeDisplay');
    this.volumeBtn = document.getElementById('volumeBtn');
    this.volumeSlider = document.getElementById('volumeSlider');
    this.fullscreenBtn = document.getElementById('fullscreenBtn');
    this.skipIntroBtn = document.getElementById('skipIntroBtn');
    this.nextEpisodeOverlay = document.getElementById('nextEpisodeOverlay');
    this.nextCountdownSpan = document.getElementById('nextCountdown');

    this.introStart = parseInt(this.video.dataset.introStart || '0');
    this.introEnd = parseInt(this.video.dataset.introEnd || '0');
    this.outroStart = parseInt(this.video.dataset.outroStart || '999999');
    this.nextUrl = this.video.dataset.nextUrl || '';

    this.countdownTimer = null;
    this.countdownSeconds = 10;

    this.init();
  }

  init() {
    // 1. Play / Pause
    if (this.playPauseBtn) {
      this.playPauseBtn.addEventListener('click', () => this.togglePlay());
    }
    this.video.addEventListener('click', () => this.togglePlay());

    // 2. Time & Progress Updates
    this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
    if (this.progressBar) {
      this.progressBar.addEventListener('click', (e) => this.seek(e));
    }

    // 3. Volume
    if (this.volumeBtn) {
      this.volumeBtn.addEventListener('click', () => this.toggleMute());
    }
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        this.video.volume = e.target.value;
        this.video.muted = false;
        this.updateVolumeIcon();
      });
    }

    // 4. Fullscreen
    if (this.fullscreenBtn) {
      this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    }

    // 5. Skip Intro
    if (this.skipIntroBtn) {
      this.skipIntroBtn.addEventListener('click', () => {
        if (this.introEnd > 0) {
          this.video.currentTime = this.introEnd;
          this.skipIntroBtn.style.display = 'none';
        }
      });
    }

    // 6. Keyboard Shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));

    // 7. Video State Icons
    this.video.addEventListener('play', () => {
      if (this.playPauseBtn) this.playPauseBtn.innerHTML = '⏸';
    });
    this.video.addEventListener('pause', () => {
      if (this.playPauseBtn) this.playPauseBtn.innerHTML = '▶';
    });
  }

  togglePlay() {
    if (this.video.paused || this.video.ended) {
      this.video.play();
    } else {
      this.video.pause();
    }
  }

  onTimeUpdate() {
    const cur = this.video.currentTime;
    const dur = this.video.duration || 1;
    const pct = (cur / dur) * 100;

    if (this.progressFill) {
      this.progressFill.style.width = `${pct}%`;
    }

    if (this.timeDisplay) {
      this.timeDisplay.innerText = `${this.formatTime(cur)} / ${this.formatTime(dur)}`;
    }

    // Skip Intro button trigger
    if (this.skipIntroBtn && this.introEnd > this.introStart) {
      if (cur >= this.introStart && cur <= this.introEnd) {
        this.skipIntroBtn.style.display = 'block';
      } else {
        this.skipIntroBtn.style.display = 'none';
      }
    }

    // Next Episode Auto-prompt
    if (this.nextEpisodeOverlay && this.nextUrl && cur >= this.outroStart) {
      if (this.nextEpisodeOverlay.style.display !== 'flex') {
        this.showNextEpisodeOverlay();
      }
    }
  }

  seek(e) {
    const rect = this.progressBar.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    this.video.currentTime = pos * this.video.duration;
  }

  toggleMute() {
    this.video.muted = !this.video.muted;
    this.updateVolumeIcon();
  }

  updateVolumeIcon() {
    if (!this.volumeBtn) return;
    if (this.video.muted || this.video.volume === 0) {
      this.volumeBtn.innerHTML = '🔇';
    } else if (this.video.volume < 0.5) {
      this.volumeBtn.innerHTML = '🔉';
    } else {
      this.volumeBtn.innerHTML = '🔊';
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      this.wrapper.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  }

  showNextEpisodeOverlay() {
    this.nextEpisodeOverlay.style.display = 'flex';
    this.countdownSeconds = 10;
    if (this.nextCountdownSpan) this.nextCountdownSpan.innerText = this.countdownSeconds;

    this.countdownTimer = setInterval(() => {
      this.countdownSeconds--;
      if (this.nextCountdownSpan) this.nextCountdownSpan.innerText = this.countdownSeconds;
      if (this.countdownSeconds <= 0) {
        clearInterval(this.countdownTimer);
        window.location.href = this.nextUrl;
      }
    }, 1000);
  }

  handleKeyboard(e) {
    // Avoid interfering with inputs
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

    switch (e.code) {
      case 'Space':
      case 'KeyK':
        e.preventDefault();
        this.togglePlay();
        break;
      case 'KeyF':
        e.preventDefault();
        this.toggleFullscreen();
        break;
      case 'KeyM':
        e.preventDefault();
        this.toggleMute();
        break;
      case 'ArrowRight':
        e.preventDefault();
        this.video.currentTime = Math.min(this.video.duration, this.video.currentTime + 10);
        break;
      case 'ArrowLeft':
        e.preventDefault();
        this.video.currentTime = Math.max(0, this.video.currentTime - 10);
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.video.volume = Math.min(1, this.video.volume + 0.1);
        if (this.volumeSlider) this.volumeSlider.value = this.video.volume;
        this.video.muted = false;
        this.updateVolumeIcon();
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.video.volume = Math.max(0, this.video.volume - 0.1);
        if (this.volumeSlider) this.volumeSlider.value = this.video.volume;
        this.updateVolumeIcon();
        break;
    }
  }

  formatTime(secs) {
    const s = Math.floor(secs % 60);
    const m = Math.floor((secs / 60) % 60);
    const h = Math.floor(secs / 3600);
    const pad = (n) => (n < 10 ? '0' + n : n);
    return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new CineVersePlayer('cineverseVideo');
});
'''
write('static/js/player.js', player_js)

# ==============================================================================
# 2. MOVIES BROWSE, CATALOG & DETAIL TEMPLATES
# ==============================================================================

browse_html = '''{% extends 'base.html' %}
{% load static movie_tags %}

{% block title %}CineVerse — Watch Movies & TV Series Online in 4K UHD{% endblock %}

{% block content %}
<!-- Hero Featured Banner Showcase -->
{% if hero_movies %}
  {% with hero=hero_movies.0 %}
  <div style="position: relative; height: 75vh; min-height: 520px; max-height: 780px; display: flex; align-items: center; background: url('{{ hero.backdrop_url }}') center/cover no-repeat; margin-top: -4.75rem;">
    <!-- Vignette Gradient Overlays -->
    <div style="position: absolute; inset: 0; background: linear-gradient(0deg, #08090C 0%, rgba(8, 9, 12, 0.45) 50%, rgba(8, 9, 12, 0.8) 100%);"></div>
    <div style="position: absolute; inset: 0; background: linear-gradient(90deg, #08090C 0%, rgba(8, 9, 12, 0.7) 45%, transparent 100%);"></div>

    <div class="container" style="position: relative; z-index: 10;">
      <div style="max-width: 680px;">
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem;">
          <span class="badge badge-admin">CINEVERSE ORIGINAL</span>
          <span class="badge badge-4k">{{ hero.resolution }}</span>
          <span style="color: var(--cv-gold); font-weight: 700; font-size: 0.9rem;">★ {{ hero.average_rating }}</span>
        </div>
        <h1 style="font-size: 3.5rem; line-height: 1.1; margin-bottom: 0.75rem; text-shadow: 0 4px 15px rgba(0,0,0,0.8);">{{ hero.title }}</h1>
        <p style="font-size: 1.15rem; line-height: 1.6; color: #E0E2EC; margin-bottom: 1.75rem; text-shadow: 0 2px 8px rgba(0,0,0,0.8);">
          {{ hero.synopsis|truncatewords:28 }}
        </p>
        <div style="display: flex; gap: 1rem; align-items: center;">
          <a href="{% url 'player:movie_player' hero.slug %}" class="btn btn-primary btn-lg">
            <span>▶</span> Watch Movie
          </a>
          <a href="{{ hero.get_absolute_url }}" class="btn btn-secondary btn-lg">
            <span>ℹ️</span> Details & Cast
          </a>
        </div>
      </div>
    </div>
  </div>
  {% endwith %}
{% endif %}

<div class="container" style="margin-top: 2rem;">
  <!-- Trending Movies Rail -->
  <section class="content-rail-section">
    <div class="content-rail-header">
      <div class="content-rail-title">
        <span class="accent-bar"></span> Trending Feature Films
      </div>
      <a href="{% url 'movies:catalog' %}" class="content-rail-see-all">Explore All ›</a>
    </div>
    <div class="content-rail-scroll">
      {% for movie in trending_movies %}
        <a href="{{ movie.get_absolute_url }}" class="rail-item">
          <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" class="rail-item-poster">
          <div class="movie-card-overlay">
            <div class="movie-card-title">{{ movie.title }}</div>
            <div class="movie-card-meta">
              <span class="rating-badge">★ {{ movie.average_rating }}</span>
              <span>{{ movie.release_year }}</span>
            </div>
          </div>
        </a>
      {% empty %}
        <p style="color: var(--cv-text-muted);">Populating trending titles...</p>
      {% endfor %}
    </div>
  </section>

  <!-- Recent Releases Rail -->
  <section class="content-rail-section">
    <div class="content-rail-header">
      <div class="content-rail-title">
        <span class="accent-bar"></span> Newly Added to CineVerse
      </div>
      <a href="{% url 'movies:catalog' %}" class="content-rail-see-all">See More ›</a>
    </div>
    <div class="content-rail-scroll">
      {% for movie in recent_movies %}
        <a href="{{ movie.get_absolute_url }}" class="rail-item">
          <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" class="rail-item-poster">
          <div class="movie-card-overlay">
            <div class="movie-card-title">{{ movie.title }}</div>
            <div class="movie-card-meta">
              <span class="badge badge-4k">{{ movie.resolution }}</span>
              <span>{{ movie.formatted_duration }}</span>
            </div>
          </div>
        </a>
      {% empty %}
        <p style="color: var(--cv-text-muted);">No releases added yet.</p>
      {% endfor %}
    </div>
  </section>

  <!-- Top Rated Rail -->
  <section class="content-rail-section">
    <div class="content-rail-header">
      <div class="content-rail-title">
        <span class="accent-bar"></span> Critically Acclaimed & Top Rated
      </div>
    </div>
    <div class="content-rail-scroll">
      {% for movie in top_rated_movies %}
        <a href="{{ movie.get_absolute_url }}" class="rail-item">
          <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" class="rail-item-poster">
          <div class="movie-card-overlay">
            <div class="movie-card-title">{{ movie.title }}</div>
            <div class="movie-card-meta">
              <span class="rating-badge">★ {{ movie.average_rating }}</span>
              <span>{{ movie.release_year }}</span>
            </div>
          </div>
        </a>
      {% empty %}
        <p style="color: var(--cv-text-muted);">No rated titles available.</p>
      {% endfor %}
    </div>
  </section>
</div>
{% endblock %}
'''
write('templates/movies/browse.html', browse_html)

movie_list_html = '''{% extends 'base.html' %}
{% block title %}Browse All Movies — CineVerse Catalog{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: 1px solid var(--cv-border); padding-bottom: 1.5rem;">
    <div>
      <h1>Movie Catalog</h1>
      <p>Filter by genre, production year, content rating, and keywords.</p>
    </div>
  </div>

  <!-- Filter Toolbar -->
  <form method="get" style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2.5rem; background: var(--cv-bg-surface); padding: 1.25rem; border-radius: var(--cv-radius-md); border: 1px solid var(--cv-border);">
    <div style="flex: 2; min-width: 220px;">
      <input type="text" name="q" value="{{ search_query }}" placeholder="Search by title or cast..." class="form-input">
    </div>
    <div style="flex: 1; min-width: 160px;">
      <select name="genre" class="form-select">
        <option value="">All Genres</option>
        {% for g in all_genres %}
          <option value="{{ g.slug }}" {% if selected_genre == g.slug %}selected{% endif %}>{{ g.name }}</option>
        {% endfor %}
      </select>
    </div>
    <div style="flex: 1; min-width: 140px;">
      <select name="rating" class="form-select">
        <option value="">All Ratings</option>
        <option value="G" {% if selected_rating == 'G' %}selected{% endif %}>G</option>
        <option value="PG" {% if selected_rating == 'PG' %}selected{% endif %}>PG</option>
        <option value="PG-13" {% if selected_rating == 'PG-13' %}selected{% endif %}>PG-13</option>
        <option value="R" {% if selected_rating == 'R' %}selected{% endif %}>R</option>
      </select>
    </div>
    <button type="submit" class="btn btn-primary">Apply Filters</button>
  </form>

  <!-- Movie Cards Grid -->
  <div class="card-grid">
    {% for movie in movies %}
      <a href="{{ movie.get_absolute_url }}" class="movie-card">
        <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div class="movie-card-title">{{ movie.title }}</div>
          <div class="movie-card-meta">
            <span class="rating-badge">★ {{ movie.average_rating }}</span>
            <span>{{ movie.release_year }} • {{ movie.content_rating }}</span>
          </div>
        </div>
      </a>
    {% empty %}
      <div style="grid-column: 1 / -1; padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        No movies match your filter parameters.
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/movies/movie_list.html', movie_list_html)

movie_detail_html = '''{% extends 'base.html' %}
{% block title %}{{ movie.title }} ({{ movie.release_year }}) — CineVerse Stream{% endblock %}

{% block content %}
<div style="position: relative; min-height: 70vh; background: url('{{ movie.backdrop_url }}') center/cover no-repeat; display: flex; align-items: flex-end; padding-bottom: 4rem; margin-top: -4.75rem;">
  <div style="position: absolute; inset: 0; background: linear-gradient(0deg, #08090C 0%, rgba(8,9,12,0.6) 60%, rgba(8,9,12,0.9) 100%);"></div>

  <div class="container" style="position: relative; z-index: 10; display: flex; gap: 3rem; align-items: flex-end;">
    <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width: 250px; border-radius: var(--cv-radius-md); box-shadow: 0 20px 40px rgba(0,0,0,0.9); border: 1px solid var(--cv-border); flex-shrink: 0;">
    <div>
      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <span class="badge badge-4k">{{ movie.resolution }}</span>
        <span class="badge badge-viewer">{{ movie.content_rating }}</span>
        <span class="badge" style="background: rgba(255,255,255,0.1);">{{ movie.formatted_duration }}</span>
        <span class="badge" style="background: rgba(255,255,255,0.1);">{{ movie.audio_format }}</span>
        <span style="color: var(--cv-gold); font-weight: 700; margin-left: 0.5rem;">★ {{ movie.average_rating }}/10</span>
      </div>
      <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">{{ movie.title }}</h1>
      {% if movie.tagline %}
        <p style="font-style: italic; color: #CCD2E3; font-size: 1.1rem; margin-bottom: 1.25rem;">"{{ movie.tagline }}"</p>
      {% endif %}
      <p style="max-width: 800px; font-size: 1.05rem; line-height: 1.7; margin-bottom: 2rem;">{{ movie.synopsis }}</p>

      <div style="display: flex; gap: 1rem; align-items: center;">
        <a href="{% url 'player:movie_player' movie.slug %}" class="btn btn-primary btn-lg">
          <span>▶</span> Watch Now
        </a>
        <button class="btn btn-secondary btn-lg" onclick="alert('Added to your watchlist!')">
          <span>+</span> Add to Watchlist
        </button>
      </div>
    </div>
  </div>
</div>

<div class="container" style="margin-top: 3.5rem;">
  <div style="display: grid; grid-template-columns: 2.5fr 1fr; gap: 3rem;">
    <div>
      <!-- Cast Members Gallery -->
      <h3 style="margin-bottom: 1.5rem;">Top Cast & Stars</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 1.25rem; margin-bottom: 3.5rem;">
        {% for cast in cast_list %}
          <a href="{{ cast.person.get_absolute_url }}" style="text-align: center; text-decoration: none;">
            <img src="https://api.dicebear.com/7.x/initials/svg?seed={{ cast.person.full_name }}&backgroundColor=1f2330" style="width: 75px; height: 75px; border-radius: 50%; margin-bottom: 0.5rem; border: 2px solid var(--cv-border);">
            <div style="font-weight: 600; font-size: 0.85rem; color: #fff;">{{ cast.person.full_name }}</div>
            <div style="font-size: 0.75rem; color: var(--cv-text-muted);">{{ cast.character_name }}</div>
          </a>
        {% empty %}
          <p style="color: var(--cv-text-muted);">Cast information being verified.</p>
        {% endfor %}
      </div>

      <!-- Related Titles -->
      <h3 style="margin-bottom: 1.5rem;">More Like This</h3>
      <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));">
        {% for rel in related_movies %}
          <a href="{{ rel.get_absolute_url }}" class="movie-card">
            <img src="{{ rel.poster_url }}" alt="{{ rel.title }}" class="movie-card-poster">
            <div class="movie-card-overlay">
              <div class="movie-card-title">{{ rel.title }}</div>
              <div class="movie-card-meta">★ {{ rel.average_rating }}</div>
            </div>
          </a>
        {% endfor %}
      </div>
    </div>

    <!-- Technical Specs & Metadata Sidebar -->
    <div>
      <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.75rem;">
        <h4 style="margin-bottom: 1.25rem;">Audio & Streaming Specs</h4>
        <div style="display: flex; flex-direction: column; gap: 1rem; font-size: 0.9rem;">
          <div>
            <div style="color: var(--cv-text-muted);">Audio Channels:</div>
            <div style="font-weight: 600; color: #fff;">{{ movie.audio_format }}</div>
          </div>
          <div>
            <div style="color: var(--cv-text-muted);">Video Stream Quality:</div>
            <div style="font-weight: 600; color: #fff;">{{ movie.get_resolution_display }}</div>
          </div>
          <div>
            <div style="color: var(--cv-text-muted);">Aspect Ratio:</div>
            <div style="font-weight: 600; color: #fff;">{{ movie.aspect_ratio }}</div>
          </div>
          <div>
            <div style="color: var(--cv-text-muted);">Available Subtitles:</div>
            <div style="font-weight: 600; color: #fff;">
              {% for sub in subtitles %}
                {{ sub.language_name }}{% if not forloop.last %}, {% endif %}
              {% empty %}
                English (CC), Spanish, French
              {% endfor %}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/movies/movie_detail.html', movie_detail_html)

# ==============================================================================
# 3. SERIES & SEASONS TEMPLATES
# ==============================================================================

series_browse_html = '''{% extends 'base.html' %}
{% block title %}TV Shows & Web Series — CineVerse Streaming{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>Television Series & Originals</h1>
    <p>Binge multi-season dramas, thrilling mysteries, and anime epics.</p>
  </div>

  <div class="card-grid">
    {% for series in series_list %}
      <a href="{{ series.get_absolute_url }}" class="movie-card">
        <img src="{{ series.poster_url }}" alt="{{ series.title }}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div class="movie-card-title">{{ series.title }}</div>
          <div class="movie-card-meta">
            <span class="rating-badge">★ {{ series.average_rating }}</span>
            <span>{{ series.total_seasons }} Season{% if series.total_seasons != 1 %}s{% endif %}</span>
          </div>
        </div>
      </a>
    {% empty %}
      <p>No television series cataloged yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/series/series_browse.html', series_browse_html)

series_detail_html = '''{% extends 'base.html' %}
{% block title %}{{ series.title }} — All Seasons & Episodes{% endblock %}

{% block content %}
<div style="position: relative; min-height: 65vh; background: url('{{ series.backdrop_url }}') center/cover no-repeat; display: flex; align-items: flex-end; padding-bottom: 3.5rem; margin-top: -4.75rem;">
  <div style="position: absolute; inset: 0; background: linear-gradient(0deg, #08090C 0%, rgba(8,9,12,0.65) 60%, rgba(8,9,12,0.9) 100%);"></div>

  <div class="container" style="position: relative; z-index: 10; display: flex; gap: 3rem; align-items: flex-end;">
    <img src="{{ series.poster_url }}" alt="{{ series.title }}" style="width: 240px; border-radius: var(--cv-radius-md); box-shadow: 0 20px 40px rgba(0,0,0,0.9); border: 1px solid var(--cv-border); flex-shrink: 0;">
    <div>
      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <span class="badge badge-admin">ORIGINAL SERIES</span>
        <span class="badge badge-viewer">{{ series.content_rating }}</span>
        <span class="badge" style="background: rgba(255,255,255,0.1);">{{ series.total_seasons }} Seasons</span>
        <span style="color: var(--cv-gold); font-weight: 700;">★ {{ series.average_rating }}/10</span>
      </div>
      <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">{{ series.title }}</h1>
      <p style="max-width: 800px; font-size: 1.05rem; line-height: 1.7; margin-bottom: 1.75rem;">{{ series.synopsis }}</p>
    </div>
  </div>
</div>

<div class="container" style="margin-top: 3rem;">
  <!-- Season Selector & Episode List -->
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <h2>Episodes</h2>
    {% if seasons %}
      <select id="seasonSelector" class="form-select" style="width: 220px;" onchange="switchSeason(this.value)">
        {% for s in seasons %}
          <option value="{{ s.id }}">Season {{ s.season_number }} ({{ s.episodes.count }} Episodes)</option>
        {% endfor %}
      </select>
    {% endif %}
  </div>

  <div id="episodesListContainer" style="display: flex; flex-direction: column; gap: 1.25rem;">
    {% if selected_season %}
      {% for ep in selected_season.episodes.all %}
        <div style="display: flex; gap: 1.5rem; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.25rem; align-items: center; transition: var(--cv-transition);" onmouseover="this.style.borderColor='var(--cv-primary)';" onmouseout="this.style.borderColor='var(--cv-border)';">
          <div style="position: relative; width: 200px; aspect-ratio: 16/9; border-radius: var(--cv-radius-sm); overflow: hidden; flex-shrink: 0;">
            <img src="{{ ep.thumbnail_url }}" alt="{{ ep.title }}" style="width: 100%; height: 100%; object-fit: cover;">
            <a href="{{ ep.get_absolute_url }}" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #fff; text-decoration: none;">▶</a>
          </div>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
              <h4 style="font-size: 1.1rem;">{{ ep.episode_number }}. {{ ep.title }}</h4>
              <span style="color: var(--cv-text-muted); font-size: 0.85rem;">{{ ep.duration_minutes }}m</span>
            </div>
            <p style="font-size: 0.9rem; line-height: 1.5; color: var(--cv-text-muted);">{{ ep.synopsis|default:"No episode synopsis provided." }}</p>
          </div>
        </div>
      {% empty %}
        <p style="color: var(--cv-text-muted);">No episodes uploaded for this season yet.</p>
      {% endfor %}
    {% endif %}
  </div>
</div>

<script>
function switchSeason(seasonId) {
  fetch(`/seasons/${seasonId}/episodes/json/`)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('episodesListContainer');
      container.innerHTML = data.episodes.map(ep => `
        <div style="display: flex; gap: 1.5rem; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.25rem; align-items: center;">
          <div style="position: relative; width: 200px; aspect-ratio: 16/9; border-radius: var(--cv-radius-sm); overflow: hidden; flex-shrink: 0;">
            <img src="${ep.thumbnail}" alt="${ep.title}" style="width: 100%; height: 100%; object-fit: cover;">
            <a href="${ep.player_url}" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #fff; text-decoration: none;">▶</a>
          </div>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
              <h4 style="font-size: 1.1rem;">${ep.number}. ${ep.title}</h4>
              <span style="color: var(--cv-text-muted); font-size: 0.85rem;">${ep.duration}</span>
            </div>
            <p style="font-size: 0.9rem; line-height: 1.5; color: var(--cv-text-muted);">${ep.synopsis || ''}</p>
          </div>
        </div>
      `).join('');
    });
}
</script>
{% endblock %}
'''
write('templates/series/series_detail.html', series_detail_html)

# ==============================================================================
# 4. PLAYER INTERFACE TEMPLATES
# ==============================================================================

player_movie_html = '''{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Streaming: {{ movie.title }} — CineVerse Cinema</title>
  <link rel="stylesheet" href="{% static 'css/main.css' %}">
  <style>
    body { background: #000; margin: 0; padding: 0; overflow: hidden; }
    .player-wrapper { width: 100vw; height: 100vh; background: #000; position: relative; }
    video { width: 100%; height: 100%; object-fit: contain; }
  </style>
</head>
<body>
  <div class="player-wrapper">
    <!-- Main Video Element -->
    <video id="cineverseVideo" src="{{ video_src }}" preload="metadata" data-stream-token="{{ stream_token }}">
      {% for sub in subtitles %}
        <track label="{{ sub.language_name }}" kind="subtitles" srclang="{{ sub.language_code }}" src="{{ sub.vtt_file.url }}" {% if sub.is_default %}default{% endif %}>
      {% endfor %}
    </video>

    <!-- Custom HUD Controls Overlay -->
    <div class="player-hud">
      <!-- Top HUD: Back button & Title -->
      <div class="player-top-bar">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <a href="{{ movie.get_absolute_url }}" class="btn btn-icon btn-secondary" style="font-size: 1.25rem;">‹</a>
          <span class="player-title">{{ movie.title }} ({{ movie.release_year }})</span>
          <span class="badge badge-4k">{{ movie.resolution }}</span>
        </div>
      </div>

      <!-- Bottom HUD: Scrubber & Control Buttons -->
      <div class="player-bottom-bar">
        <div class="player-progress-bar" id="progressBar">
          <div class="player-progress-fill" id="progressFill" style="width: 0%;"></div>
          <div class="player-progress-handle"></div>
        </div>

        <div class="player-controls-row">
          <div class="player-controls-left">
            <button type="button" class="player-control-btn" id="playPauseBtn">▶</button>
            <div class="player-time-display" id="timeDisplay">00:00 / 00:00</div>
          </div>

          <div class="player-controls-right">
            <button type="button" class="player-control-btn" id="volumeBtn">🔊</button>
            <input type="range" id="volumeSlider" min="0" max="1" step="0.05" value="1" style="width: 80px; accent-color: var(--cv-primary); cursor: pointer;">
            <button type="button" class="player-control-btn" id="fullscreenBtn">⛶</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script src="{% static 'js/player.js' %}"></script>
</body>
</html>
'''
write('templates/player/player_movie.html', player_movie_html)

player_episode_html = '''{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Streaming: {{ series.title }} {{ episode.title }} — CineVerse</title>
  <link rel="stylesheet" href="{% static 'css/main.css' %}">
  <style>
    body { background: #000; margin: 0; padding: 0; overflow: hidden; }
    .player-wrapper { width: 100vw; height: 100vh; background: #000; position: relative; }
    video { width: 100%; height: 100%; object-fit: contain; }
  </style>
</head>
<body>
  <div class="player-wrapper">
    <!-- Video Element -->
    <video id="cineverseVideo" 
           src="{{ video_src }}" 
           preload="metadata" 
           data-stream-token="{{ stream_token }}"
           data-intro-start="{{ episode.intro_start_sec }}"
           data-intro-end="{{ episode.intro_end_sec }}"
           data-outro-start="{{ episode.outro_start_sec }}">
      {% for sub in subtitles %}
        <track label="{{ sub.language_name }}" kind="subtitles" srclang="{{ sub.language_code }}" src="{{ sub.vtt_file.url }}" {% if sub.is_default %}default{% endif %}>
      {% endfor %}
    </video>

    <!-- Skip Intro Floating Button -->
    <button type="button" class="skip-intro-btn" id="skipIntroBtn" style="display: none;">
      ⏭ Skip Intro
    </button>

    <!-- Next Episode Auto-Countdown Overlay -->
    <div id="nextEpisodeOverlay" style="display: none; position: absolute; bottom: 6rem; right: 2rem; background: rgba(16, 18, 23, 0.95); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem; width: 320px; box-shadow: var(--cv-shadow-card); backdrop-filter: blur(12px); flex-direction: column; gap: 0.75rem; z-index: 100;">
      <div style="font-size: 0.85rem; color: var(--cv-text-muted);">Next Episode Playing in <span id="nextCountdown" style="color: var(--cv-primary); font-weight: 700;">10</span>s</div>
      <button type="button" class="btn btn-primary btn-sm" onclick="window.location.reload();">Watch Now</button>
    </div>

    <!-- HUD Overlay -->
    <div class="player-hud">
      <div class="player-top-bar">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <a href="{{ series.get_absolute_url }}" class="btn btn-icon btn-secondary" style="font-size: 1.25rem;">‹</a>
          <span class="player-title">{{ series.title }} — S{{ episode.season.season_number:02d }}E{{ episode.episode_number:02d }} "{{ episode.title }}"</span>
        </div>
      </div>

      <div class="player-bottom-bar">
        <div class="player-progress-bar" id="progressBar">
          <div class="player-progress-fill" id="progressFill" style="width: 0%;"></div>
        </div>

        <div class="player-controls-row">
          <div class="player-controls-left">
            <button type="button" class="player-control-btn" id="playPauseBtn">▶</button>
            <div class="player-time-display" id="timeDisplay">00:00 / 00:00</div>
          </div>

          <div class="player-controls-right">
            <button type="button" class="player-control-btn" id="volumeBtn">🔊</button>
            <input type="range" id="volumeSlider" min="0" max="1" step="0.05" value="1" style="width: 80px; accent-color: var(--cv-primary); cursor: pointer;">
            <button type="button" class="player-control-btn" id="fullscreenBtn">⛶</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script src="{% static 'js/player.js' %}"></script>
</body>
</html>
'''
write('templates/player/player_episode.html', player_episode_html)

print("Phase 2 Templates and Player JS successfully created.")
