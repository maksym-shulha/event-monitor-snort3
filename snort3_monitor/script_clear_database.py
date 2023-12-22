import logging
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Event


logger = logging.getLogger('monitor')


if __name__ == '__main__':
    Event.objects.all().delete()
    logger.info('All events have been deleted')
