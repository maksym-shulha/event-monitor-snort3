import json
import logging
import os
import threading
import time
from datetime import datetime
from json import JSONDecodeError

import django
from django.http import Http404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Event, Rule


logger = logging.getLogger('events')
formatter = logging.Formatter('%(name)s -> %(levelname)s : %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


class OnMyWatch:
    """Watch into directory with logs

    Responsible to check log file for changes.
    watch_file -- location of log file
    current_position_file -- name of file with current position
    """
    watch_file: str = '/var/log/snort/alert_json.txt'
    current_position_file: str = 'current_position.txt'

    def __init__(self):
        """Create Lock for instance"""
        self.lock = threading.Lock()

    def run(self):
        """Start watch in log file"""
        logger.info('Running.')
        try:
            while True:
                if os.path.exists(self.watch_file):
                    self.read_data()
                else:
                    logger.error('Watch file does not exist.')
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info('Stopped.')

    def read_data(self):
        """Open file and read data"""
        try:
            with self.lock:
                with open(self.watch_file, encoding='latin-1') as file:
                    file.seek(self.get_current_position())
                    new_data = file.readlines()
                    self.save_current_position(file.tell())

                if new_data:
                    self.save_data(new_data)

        except PermissionError:
            logger.error(f'Set up permissions for {self.watch_file}!')

    @staticmethod
    def save_data(data: list):
        """Save data into database"""
        for line in data:
            try:
                event_data = json.loads(line)

                # drop unuseful fields
                allowed_fields = ['src_addr', 'src_port', 'dst_addr', 'dst_port',
                                  'proto', 'seconds', 'sid', 'rev', 'gid']
                event_data = {key: value for key, value in event_data.items() if key in allowed_fields}

                # save event
                timestamp = datetime.fromtimestamp(event_data.pop('seconds'))
                rule = Rule.get_rule(event_data.pop('sid'), event_data.pop('rev'), event_data.pop('gid'))
                new_event = Event(**event_data)
                new_event.rule = rule
                new_event.timestamp = timestamp
                new_event.save()

            except KeyError:
                logger.error(f'Event has no full required information: {line}')
            except Http404:
                logger.error(f'There is no Rule matches with event: {line}')
            except JSONDecodeError:
                logger.error(f'There is decoding error: {line}')

    @classmethod
    def get_current_position(cls) -> int:
        """Get current position from file if it already exists."""
        try:
            with open(cls.current_position_file, 'r') as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    @classmethod
    def save_current_position(cls, position: int):
        """Save current position"""
        with open(cls.current_position_file, 'w') as f:
            f.write(str(position))


if __name__ == '__main__':
    watcher = OnMyWatch()
    watcher.run()
