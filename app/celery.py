from celery.schedules import crontab
from celery.schedules import crontab

from celery import Celery

celery_app = Celery(
    "telegram_bot",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    timezone="Asia/Tehran",
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url="redis://localhost:6379/0",
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.beat_schedule = {

}
