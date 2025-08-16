from celery import Celery
from config import settings

celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuración opcional: reintentos, timezone, etc.
celery.conf.update(
    task_time_limit=60,
    task_acks_late=True,
)
