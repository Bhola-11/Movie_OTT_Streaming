# CineVerse — Movie & OTT Streaming Management Platform

CineVerse is an enterprise-grade digital cinema and OTT streaming management platform engineered on the Django MVT architecture. It features high-performance adaptive streaming telemetry, multi-season television hierarchy, real-time playback progress sync, cryptographic stream token validation, multi-tier subscription billing with ReportLab PDF tax invoices, and executive platform analytics.

---

## Dependencies

The platform relies on the following core dependencies:

- **Python**: Version 3.11+
- **Django**: Version 5.0.6
- **Database**: SQLite (Development) / PostgreSQL 15+ (Production)
- **Cache & Message Broker**: Redis 7.0+
- **Background Worker**: Celery 5.4.0
- **Document Engine**: ReportLab 4.2.0 (PDF Tax Invoice generation)
- **WSGI / Web Server**: Gunicorn 22.0.0 & Nginx Alpine
- **Frontend HUD**: Vanilla ES6+ and custom CSS3 variables (dark OTT design system)

---

## Installation

### 1. Clone or Extract the Repository
```bash
cd CineVerse_Movie_OTT_Streaming
```

### 2. Setup Python Virtual Environment
```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Node Frontend Build Dependencies
```bash
npm install
```

---

## Build

### 1. Database Migrations
Apply initial database migrations across all 18 domain applications:
```bash
python manage.py migrate
```

### 2. Static Asset Collection
Compile and collect static assets for production:
```bash
python manage.py collectstatic --noinput
```

### 3. Docker Container Build (Optional)
To build containerized images for multi-container deployment:
```bash
docker build -t cineverse-web:latest .
docker compose build
```

---

## Run

### Option A: Local Development Server
1. Seed the catalog with realistic movies, TV shows, tiers, and users:
   ```bash
   python manage.py seed_cineverse
   ```
2. Start the development HTTP server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
3. Open your browser and navigate to `http://127.0.0.1:8000/`.

### Option B: Docker Compose Multi-Service Stack
To launch Django, Redis, Celery Worker, Celery Beat, and Nginx reverse proxy:
```bash
docker compose up -d
```

---

## Usage & Credentials

### Default Administrative & Subscriber Access
- **System Administrator**:
  - Email: `admin@cineverse.io`
  - Password: `Admin12345!`
  - Portal: `http://127.0.0.1:8000/admin/` and `http://127.0.0.1:8000/analytics/`
- **Subscriber / Viewer**:
  - Email: `viewer@cineverse.io`
  - Password: `Viewer12345!`
  - Portal: `http://127.0.0.1:8000/movies/`

### Key Platform Routes
- **Content Catalog & Discovery**: `http://127.0.0.1:8000/movies/`
- **Continue Watching Shelf**: Displayed dynamically on the home browse feed
- **TV Series & Seasons**: `http://127.0.0.1:8000/series/`
- **Membership & Pricing**: `http://127.0.0.1:8000/subscriptions/plans/`
- **PDF Tax Invoices**: `http://127.0.0.1:8000/payments/invoices/`
- **AI Recommendation Feed**: `http://127.0.0.1:8000/recommendations/`
- **Executive Analytics KPI Hub**: `http://127.0.0.1:8000/analytics/`
- **Content Moderation Queue**: `http://127.0.0.1:8000/moderation/queue/`
- **Security Audit Logs**: `http://127.0.0.1:8000/audit/`

---

## Automated Testing

Run the full automated test suite using `pytest`:
```bash
pytest tests/ -v
```

---

## Proprietary Notice

All rights reserved. CineVerse and associated streaming media architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or commercial exploitation is strictly prohibited.
