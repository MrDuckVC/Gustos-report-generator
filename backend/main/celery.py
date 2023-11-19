import os
from logging.config import dictConfig

from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")

app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(**kwargs):
    dictConfig(settings.LOGGING)


app.autodiscover_tasks()
