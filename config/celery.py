import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.settings.dev")

app = Celery("myproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
