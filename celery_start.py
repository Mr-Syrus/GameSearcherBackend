
from celery.schedules import crontab

import config
import incelization

# Initialization
incelization.init()

celery_app = config.CELERY_APP

celery_app.conf.beat_schedule = {

}
