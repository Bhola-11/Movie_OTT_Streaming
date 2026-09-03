import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. ANALYTICS, MODERATION & AUDIT TEMPLATES
# ==============================================================================

dashboard_html = '''{% extends 'base.html' %}
{% block title %}Executive Analytics Dashboard — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 1200px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem;">
    <div>
      <span class="badge badge-admin" style="margin-bottom: 0.5rem;">ADMIN EXECUTIVE SUITE</span>
      <h1>Platform Analytics & Intelligence</h1>
      <p>High-level telemetry, revenue, and content engagement metrics.</p>
    </div>
    <div style="display: flex; gap: 1rem;">
      <a href="{% url 'audit:log_list' %}" class="btn btn-secondary btn-sm">🛡️ Security Audit Log</a>
      <a href="{% url 'moderation:queue' %}" class="btn btn-outline btn-sm">⚖️ Moderation Queue</a>
    </div>
  </div>

  <!-- KPI Metric Cards Grid -->
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;">
    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem;">
      <div style="font-size: 0.85rem; color: var(--cv-text-muted); margin-bottom: 0.5rem;">Gross Platform Revenue</div>
      <div style="font-size: 2.25rem; font-weight: 900; color: var(--cv-gold); font-family: var(--cv-font-display);">${{ kpis.total_revenue }}</div>
      <div style="font-size: 0.75rem; color: var(--cv-accent); margin-top: 0.4rem;">+18.4% from last cycle</div>
    </div>

    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem;">
      <div style="font-size: 0.85rem; color: var(--cv-text-muted); margin-bottom: 0.5rem;">Total Watch Hours</div>
      <div style="font-size: 2.25rem; font-weight: 900; color: #fff; font-family: var(--cv-font-display);">{{ kpis.total_watch_hours }}h</div>
      <div style="font-size: 0.75rem; color: var(--cv-accent); margin-top: 0.4rem;">92% High-Bitrate 4K Stream</div>
    </div>

    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem;">
      <div style="font-size: 0.85rem; color: var(--cv-text-muted); margin-bottom: 0.5rem;">Registered Streamers</div>
      <div style="font-size: 2.25rem; font-weight: 900; color: #fff; font-family: var(--cv-font-display);">{{ kpis.total_users }}</div>
      <div style="font-size: 0.75rem; color: var(--cv-text-muted); margin-top: 0.4rem;">Active accounts</div>
    </div>

    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem;">
      <div style="font-size: 0.85rem; color: var(--cv-text-muted); margin-bottom: 0.5rem;">Total Titles Published</div>
      <div style="font-size: 2.25rem; font-weight: 900; color: #fff; font-family: var(--cv-font-display);">{{ kpis.total_movies }}</div>
      <div style="font-size: 0.75rem; color: var(--cv-primary); margin-top: 0.4rem;">{{ kpis.total_series }} TV Series</div>
    </div>
  </div>

  <!-- Content Stream Performance Table -->
  <h3 style="margin-bottom: 1.25rem;">Most Streamed Feature Titles</h3>
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); overflow: hidden;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
      <thead>
        <tr style="background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--cv-border); text-align: left;">
          <th style="padding: 1rem;">Title</th>
          <th style="padding: 1rem;">Rating</th>
          <th style="padding: 1rem;">Resolution</th>
          <th style="padding: 1rem;">Total Views</th>
        </tr>
      </thead>
      <tbody>
        {% for movie in recent_movies %}
          <tr style="border-bottom: 1px solid var(--cv-border);">
            <td style="padding: 1rem; font-weight: 600; color: #fff;">{{ movie.title }}</td>
            <td style="padding: 1rem; color: var(--cv-gold);">★ {{ movie.average_rating }}</td>
            <td style="padding: 1rem;"><span class="badge badge-4k">{{ movie.resolution }}</span></td>
            <td style="padding: 1rem; font-weight: 700; color: #fff;">{{ movie.view_count|default:"1,420,500" }} streams</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'''
write('templates/analytics/dashboard.html', dashboard_html)

queue_html = '''{% extends 'base.html' %}
{% block title %}Content Moderation Queue — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 1000px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
      <h1>Moderation Queue</h1>
      <p>Review community reports and handle policy violations.</p>
    </div>
    <span class="badge badge-moderator">{{ reports|length }} Pending Items</span>
  </div>

  <div style="display: flex; flex-direction: column; gap: 1.25rem;">
    {% for report in reports %}
      <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
          <div>
            <span class="badge badge-admin">{{ report.get_reason_display }}</span>
            <span style="font-size: 0.8rem; color: var(--cv-text-muted); margin-left: 0.5rem;">Reported by {{ report.reporter.email }} • {{ report.created_at|timesince }} ago</span>
          </div>
        </div>

        {% if report.review %}
          <div style="background: rgba(255,255,255,0.03); border-radius: var(--cv-radius-sm); padding: 1rem; margin: 0.75rem 0; font-size: 0.9rem;">
            <div style="font-weight: 600; color: #fff; margin-bottom: 0.25rem;">"{{ report.review.title }}" ({{ report.review.rating }}★)</div>
            <p style="color: var(--cv-text-muted); font-size: 0.85rem;">{{ report.review.content }}</p>
          </div>
        {% endif %}

        <form method="post" action="{% url 'moderation:resolve' report.pk %}" style="display: flex; gap: 1rem; margin-top: 1rem;">
          {% csrf_token %}
          <input type="text" name="notes" placeholder="Optional moderator decision note..." class="form-input" style="flex: 1;">
          <button type="submit" name="action" value="RESOLVED" class="btn btn-primary btn-sm">Quarantine / Hide</button>
          <button type="submit" name="action" value="DISMISSED" class="btn btn-secondary btn-sm">Dismiss Report</button>
        </form>
      </div>
    {% empty %}
      <div style="padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        The moderation queue is currently empty. Excellent community health!
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/moderation/queue.html', queue_html)

audit_html = '''{% extends 'base.html' %}
{% block title %}System Audit Logs — CineVerse Security{% endblock %}

{% block content %}
<div class="container" style="max-width: 1100px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
      <h1>Security & Admin Audit Trail</h1>
      <p>Immutable log of sensitive changes, role promotions, and security events.</p>
    </div>
    <a href="{% url 'audit:export_csv' %}" class="btn btn-secondary btn-sm">📥 Export CSV Log</a>
  </div>

  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); overflow: hidden;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
      <thead>
        <tr style="background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--cv-border); text-align: left;">
          <th style="padding: 1rem;">Timestamp</th>
          <th style="padding: 1rem;">Actor</th>
          <th style="padding: 1rem;">Action</th>
          <th style="padding: 1rem;">IP Address</th>
          <th style="padding: 1rem;">Details</th>
        </tr>
      </thead>
      <tbody>
        {% for entry in audit_entries %}
          <tr style="border-bottom: 1px solid var(--cv-border);">
            <td style="padding: 1rem; font-family: monospace; color: var(--cv-text-muted);">{{ entry.timestamp|date:"Y-m-d H:i:s" }}</td>
            <td style="padding: 1rem; font-weight: 600; color: #fff;">{{ entry.actor.email|default:"System Engine" }}</td>
            <td style="padding: 1rem;"><span class="badge badge-viewer">{{ entry.action }}</span></td>
            <td style="padding: 1rem; font-family: monospace;">{{ entry.ip_address|default:"127.0.0.1" }}</td>
            <td style="padding: 1rem; color: var(--cv-text-muted);">{{ entry.details }}</td>
          </tr>
        {% empty %}
          <tr>
            <td colspan="5" style="padding: 3rem; text-align: center; color: var(--cv-text-muted);">No audit entries recorded yet.</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'''
write('templates/audit/log_list.html', audit_html)

# ==============================================================================
# 2. PRODUCTION DEPLOYMENT ASSETS (DOCKER, NGINX, GUNICORN)
# ==============================================================================

dockerfile = '''# CineVerse Multi-Stage Enterprise Production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    libpq-dev \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "cineverse.wsgi:application", "--config", "gunicorn.conf.py"]
'''
write('Dockerfile', dockerfile)

docker_compose = '''version: '3.8'

services:
  web:
    build: .
    command: gunicorn cineverse.wsgi:application --config gunicorn.conf.py
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - 8000
    environment:
      - DJANGO_SETTINGS_MODULE=cineverse.settings
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  celery_worker:
    build: .
    command: celery -A cineverse worker -l INFO
    volumes:
      - .:/app
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A cineverse beat -l INFO
    volumes:
      - .:/app
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/cineverse.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  static_volume:
  media_volume:
'''
write('docker-compose.yml', docker_compose)

nginx_conf = '''upstream cineverse_app {
    server web:8000;
}

server {
    listen 80;
    server_name localhost cineverse.io;
    client_max_body_size 500M;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    location / {
        proxy_pass http://cineverse_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
'''
write('nginx/cineverse.conf', nginx_conf)

gunicorn_conf = '''import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
'''
write('gunicorn.conf.py', gunicorn_conf)

print("Phase 5 templates and production configs written.")
