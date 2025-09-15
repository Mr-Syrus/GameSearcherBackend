
from celery.schedules import crontab

import config
import incelization

# Initialization
incelization.init()

celery_app = config.CELERY_APP

celery_app.conf.beat_schedule = {
    'task-scheduler_user_games': {
        'task': 'task.steam_virtual_user.user_games.scheduler_user_games',
        'schedule': crontab(minute="0", hour="1"),
    },
}
