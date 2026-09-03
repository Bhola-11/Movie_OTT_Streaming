import os

apps = [
    'movies', 'series', 'seasons', 'episodes', 'player', 'history',
    'watchlist', 'reviews', 'recommendations', 'subscriptions',
    'payments', 'notifications', 'analytics', 'moderation', 'audit'
]

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

for app in apps:
    class_name = f"{app.capitalize()}Config"
    apps_content = f"""from django.apps import AppConfig

class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app}'
"""
    write(f"{app}/apps.py", apps_content)
    write(f"{app}/__init__.py", "")
    write(f"{app}/models.py", "from django.db import models\n")
    write(f"{app}/views.py", "from django.shortcuts import render\n")
    write(f"{app}/urls.py", f"""from django.urls import path
from . import views

app_name = '{app}'

urlpatterns = []
""")
    write(f"{app}/admin.py", "from django.contrib import admin\n")

print("All app stubs initialized successfully.")
