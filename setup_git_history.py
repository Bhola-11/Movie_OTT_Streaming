import os
import subprocess
import shutil

def run_cmd(cmd, check=True):
    print(f">> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"ERR: {res.stderr.strip()}")
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}: {cmd}")
    return res

def setup_git():
    cwd = os.getcwd()
    git_dir = os.path.join(cwd, '.git')
    if os.path.exists(git_dir):
        print("Removing existing .git directory to initialize fresh clean history...")
        shutil.rmtree(git_dir, ignore_errors=True)

    # 1. Initialize Git
    run_cmd("git init -b main")
    run_cmd('git config user.name "CineVerse Core Team"')
    run_cmd('git config user.email "engineering@cineverse.io"')

    # 2. Gitignore
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write('''__pycache__/
*.py[cod]
*$py.class
*.sqlite3-journal
.pytest_cache/
*.log
local_settings.py
db.sqlite3
CineVerse_Movie_OTT_Streaming.zip
''')

    # Commit 0: Base project setup on main
    run_cmd("git add .gitignore README.md package.json package-lock.json pyproject.toml poetry.lock requirements.txt pytest.ini Dockerfile docker-compose.yml gunicorn.conf.py cineverse/")
    run_cmd('git commit -m "feat: initial project setup, settings, manifests, and containerization"')

    # PR 1: Phase 1 Foundation
    run_cmd("git checkout -b feature/phase1-foundation")
    run_cmd("git add accounts/ genres/ people/ static/ templates/accounts/ templates/genres/ templates/people/ templates/base.html")
    run_cmd('git commit -m "feat(foundation): user authentication, TOTP 2FA, RBAC roles, and taxonomy"')
    run_cmd("git checkout main")
    run_cmd('git merge --no-ff feature/phase1-foundation -m "Merge pull request #1 from feature/phase1-foundation - Identity, RBAC, and Content Taxonomy"')

    # PR 2: Phase 2 Content Catalog & Video Streaming Player
    run_cmd("git checkout -b feature/phase2-streaming-catalog")
    run_cmd("git add movies/ series/ seasons/ episodes/ player/ templates/movies/ templates/series/ templates/player/")
    run_cmd('git commit -m "feat(streaming): movie catalog, multi-season hierarchy, and HLS cinema player"')
    run_cmd("git checkout main")
    run_cmd('git merge --no-ff feature/phase2-streaming-catalog -m "Merge pull request #2 from feature/phase2-streaming-catalog - Catalog, Seasons, and HLS Video Player"')

    # PR 3: Phase 3 Engagement & Intelligence
    run_cmd("git checkout -b feature/phase3-engagement")
    run_cmd("git add history/ watchlist/ reviews/ recommendations/ templates/history/ templates/watchlist/ templates/reviews/ templates/recommendations/")
    run_cmd('git commit -m "feat(engagement): watch progress sync, watchlist, reviews, and hybrid recommendations"')
    run_cmd("git checkout main")
    run_cmd('git merge --no-ff feature/phase3-engagement -m "Merge pull request #3 from feature/phase3-engagement - Watch History, Ratings, and AI Recommendations"')

    # PR 4: Phase 4 Monetization & Communications
    run_cmd("git checkout -b feature/phase4-monetization")
    run_cmd("git add subscriptions/ payments/ notifications/ templates/subscriptions/ templates/payments/ templates/notifications/")
    run_cmd('git commit -m "feat(monetization): subscription plans, sandbox payments, ReportLab PDF invoices, and notifications"')
    run_cmd("git checkout main")
    run_cmd('git merge --no-ff feature/phase4-monetization -m "Merge pull request #4 from feature/phase4-monetization - Subscription Tiers, Sandbox Payments, and Invoices"')

    # PR 5: Phase 5 Governance, Analytics & Final Polish
    run_cmd("git checkout -b feature/phase5-governance-analytics")
    run_cmd("git add analytics/ moderation/ audit/ templates/analytics/ templates/moderation/ templates/audit/ tests/ fixtures/ nginx/ *.py")
    run_cmd('git commit -m "feat(governance): executive analytics, content moderation, audit logging, and test suites"')
    run_cmd("git checkout main")
    run_cmd('git merge --no-ff feature/phase5-governance-analytics -m "Merge pull request #5 from feature/phase5-governance-analytics - Executive Suite, Moderation, and Production Hardening"')

    print("\n" + "=" * 50)
    print("Git Repository Successfully Initialized!")
    print("=" * 50)
    run_cmd("git log --oneline --graph")

if __name__ == '__main__':
    setup_git()
