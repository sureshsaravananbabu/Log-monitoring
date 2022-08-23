import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logs.settings')

app = Celery('logs',
             include=['monitor.task'])

app.conf.enable_utc=False
app.conf.update(timezone="Asia/Kollata")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule={
    'every-2-seconds' : {
        'task':'monitor.task.send_notification',
        'schedule':2,
        'args':("File Path",)
    }
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
 
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
