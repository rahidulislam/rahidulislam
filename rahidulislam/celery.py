import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rahidulislam.settings')
app = Celery('rahidulislam')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()