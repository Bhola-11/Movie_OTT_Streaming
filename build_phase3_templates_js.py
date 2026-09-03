import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. HISTORY TEMPLATES
# ==============================================================================

history_html = '''{% extends 'base.html' %}
{% block title %}Watch History — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 1000px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
      <h1>Watch History</h1>
      <p>Resume where you left off or review past watched movies and series.</p>
    </div>
    {% if history_records %}
      <form method="post" action="{% url 'history:clear' %}" onsubmit="return confirm('Clear your entire watch history?');">
        {% csrf_token %}
        <button type="submit" class="btn btn-outline btn-sm" style="color: #FF5E62; border-color: rgba(255,94,98,0.4);">
          Clear All History
        </button>
      </form>
    {% endif %}
  </div>

  <div style="display: flex; flex-direction: column; gap: 1.25rem;">
    {% for record in history_records %}
      <div style="display: flex; gap: 1.5rem; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.25rem; align-items: center;">
        <div style="position: relative; width: 180px; aspect-ratio: 16/9; border-radius: var(--cv-radius-sm); overflow: hidden; flex-shrink: 0;">
          <img src="{{ record.target_thumbnail }}" alt="{{ record.target_title }}" style="width: 100%; height: 100%; object-fit: cover;">
          <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: rgba(255,255,255,0.2);">
            <div style="height: 100%; width: {{ record.percentage_watched }}%; background: var(--cv-primary);"></div>
          </div>
        </div>

        <div style="flex: 1;">
          <h4 style="font-size: 1.1rem; margin-bottom: 0.3rem;">{{ record.target_title }}</h4>
          <div style="font-size: 0.825rem; color: var(--cv-text-muted); margin-bottom: 0.75rem;">
            Watched {{ record.percentage_watched|floatformat:0 }}% • {{ record.last_watched_at|timesince }} ago • on {{ record.device_type }}
          </div>
          <a href="{{ record.resume_url }}" class="btn btn-primary btn-sm">
            <span>▶</span> Resume Watching
          </a>
        </div>
      </div>
    {% empty %}
      <div style="padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        You haven't watched any titles yet. Start exploring movies or series!
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/history/stream_history.html', history_html)

# ==============================================================================
# 2. WATCHLIST & FAVORITES TEMPLATES
# ==============================================================================

watchlist_html = '''{% extends 'base.html' %}
{% block title %}My Watchlist — CineVerse{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>My Watchlist</h1>
    <p>Titles you've saved to stream later on CineVerse.</p>
  </div>

  <div class="card-grid">
    {% for item in items %}
      <a href="{{ item.content_url }}" class="movie-card">
        <img src="{{ item.content_poster }}" alt="{{ item.content_title }}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div class="movie-card-title">{{ item.content_title }}</div>
          <div class="movie-card-meta">Added {{ item.added_at|timesince }} ago</div>
        </div>
      </a>
    {% empty %}
      <div style="grid-column: 1 / -1; padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        Your watchlist is empty. Add titles while browsing movies and TV shows!
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/watchlist/my_list.html', watchlist_html)

favorites_html = '''{% extends 'base.html' %}
{% block title %}My Favorite Titles — CineVerse{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>Liked & Favorite Titles</h1>
    <p>Titles you have given a thumbs up or starred.</p>
  </div>

  <div class="card-grid">
    {% for fav in favorites %}
      <a href="{% if fav.movie %}{{ fav.movie.get_absolute_url }}{% else %}{{ fav.series.get_absolute_url }}{% endif %}" class="movie-card">
        <img src="{% if fav.movie %}{{ fav.movie.poster_url }}{% else %}{{ fav.series.poster_url }}{% endif %}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div class="movie-card-title">{% if fav.movie %}{{ fav.movie.title }}{% else %}{{ fav.series.title }}{% endif %}</div>
        </div>
      </a>
    {% empty %}
      <div style="grid-column: 1 / -1; padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        No favorites recorded yet.
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/watchlist/favorites.html', favorites_html)

# ==============================================================================
# 3. REVIEWS TEMPLATES
# ==============================================================================

create_review_html = '''{% extends 'base.html' %}
{% block title %}Write a Critique / Review — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 650px; padding-top: 2rem;">
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem;">
    <h2 style="margin-bottom: 0.5rem;">Submit Your Review</h2>
    <p style="margin-bottom: 2rem;">Share your honest rating and analysis with fellow film lovers.</p>

    <form method="post" action="{% url 'reviews:create' %}">
      {% csrf_token %}
      {% if request.GET.movie %}
        <input type="hidden" name="movie_slug" value="{{ request.GET.movie }}">
      {% elif request.GET.series %}
        <input type="hidden" name="series_slug" value="{{ request.GET.series }}">
      {% endif %}

      <div class="form-group">
        <label class="form-label">Rating (Out of 10)</label>
        {{ form.rating }}
      </div>

      <div class="form-group">
        <label class="form-label">Review Headline</label>
        {{ form.title }}
      </div>

      <div class="form-group">
        <label class="form-label">Critique & Detailed Thoughts</label>
        {{ form.content }}
      </div>

      <div class="form-group" style="margin-top: 1rem;">
        <label style="display: flex; align-items: center; gap: 0.5rem; color: #fff; cursor: pointer;">
          {{ form.contains_spoilers }} Warning: This review contains major plot spoilers
        </label>
      </div>

      <button type="submit" class="btn btn-primary" style="margin-top: 1.5rem; width: 100%;">Publish Review</button>
    </form>
  </div>
</div>
{% endblock %}
'''
write('templates/reviews/create_review.html', create_review_html)

# ==============================================================================
# 4. RECOMMENDATIONS FOR YOU & TOP 10 TEMPLATES
# ==============================================================================

for_you_html = '''{% extends 'base.html' %}
{% block title %}Recommended For You — CineVerse Engine{% endblock %}

{% block content %}
<div class="container" style="padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <span class="badge badge-admin" style="margin-bottom: 0.5rem;">CineVerse AI Engine</span>
    <h1>Top Picks For You</h1>
    <p>Personalized matches generated from your viewing taste, favorite genres, and community ratings.</p>
  </div>

  <div class="card-grid">
    {% for movie in recommendations %}
      <a href="{{ movie.get_absolute_url }}" class="movie-card">
        <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" class="movie-card-poster">
        <div class="movie-card-overlay">
          <div style="margin-bottom: 0.4rem;">
            <span class="badge" style="background: var(--cv-accent); color: #000; font-weight: 800;">98% MATCH</span>
          </div>
          <div class="movie-card-title">{{ movie.title }}</div>
          <div class="movie-card-meta">★ {{ movie.average_rating }} • {{ movie.release_year }}</div>
        </div>
      </a>
    {% empty %}
      <p>Start watching titles to personalize your recommendation feed!</p>
    {% endfor %}
  </div>

  <div style="margin-top: 4rem;">
    <h2>Top 10 in CineVerse Today</h2>
    <p style="margin-bottom: 2rem;">The most watched titles in the last 24 hours.</p>

    <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));">
      {% for top in top_10 %}
        <a href="{{ top.get_absolute_url }}" class="movie-card" style="position: relative;">
          <div style="position: absolute; top: -10px; left: 10px; font-size: 3.5rem; font-family: var(--cv-font-display); font-weight: 900; color: #fff; text-shadow: 0 0 20px rgba(0,0,0,0.9), 0 0 10px var(--cv-primary); z-index: 30;">
            #{{ forloop.counter }}
          </div>
          <img src="{{ top.poster_url }}" alt="{{ top.title }}" class="movie-card-poster">
          <div class="movie-card-overlay">
            <div class="movie-card-title">{{ top.title }}</div>
            <div class="movie-card-meta">{{ top.view_count }} streams</div>
          </div>
        </a>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/recommendations/for_you.html', for_you_html)

# ==============================================================================
# 5. UPDATE PLAYER JS WITH HEARTBEAT PROGRESS SYNC
# ==============================================================================

with open('static/js/player.js', 'a', encoding='utf-8') as f:
    f.write('''
// Auto Beacon Progress Sync Every 5 Seconds
setInterval(() => {
  const video = document.getElementById('cineverseVideo');
  if (video && !video.paused && video.duration > 0) {
    const urlParts = window.location.pathname.split('/');
    let contentType = 'MOVIE';
    let contentId = video.dataset.contentId || '';

    // If on episode or movie player, sync to backend
    fetch('/history/api/progress/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || ''
      },
      body: JSON.stringify({
        content_type: contentType,
        content_id: contentId,
        position_seconds: Math.floor(video.currentTime),
        duration_seconds: Math.floor(video.duration)
      })
    }).catch(() => {});
  }
}, 5000);
''')

print("Phase 3 templates and JS extensions updated.")
