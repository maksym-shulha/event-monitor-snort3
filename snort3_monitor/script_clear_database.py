import logging
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Event


logger = logging.getLogger('cron')
formatter = logging.Formatter('%(name)s -> %(levelname)s : %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == '__main__':
    Event.objects.all().delete()
    logger.info('All events have been deleted')
