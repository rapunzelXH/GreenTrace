# config/celery.py
# Celery configuration for GreenTrace background tasks.
# UC-21: daily overdue milestone check
# UC-17: weekly notification digest

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("greentrace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
