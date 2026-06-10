from celery import Celery
from kombu import Exchange, Queue
from app.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "bidpilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30*60,
    task_soft_time_limit=25*60,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Queue configuration
celery_app.conf.task_queues = (
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
)

# Default queue
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

logger.info("Celery configured")
