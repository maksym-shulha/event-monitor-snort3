import json
import logging
import os
import time
from datetime import datetime
from json import JSONDecodeError

import django
from django.http import Http404
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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
    watchDirectory = '/var/log/snort/'

    def __init__(self):
        self.observer = Observer()

    def run(self) -> None:
        """Start of watching into a directory"""
        event_handler = Handler()
        self.observer.schedule(event_handler,
                               self.watchDirectory,
                               recursive=False
                               )
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Class for handling changes in directory.
    Queue will be useful for multifile monitoring.
    """
    current_position = 0
    queue = True

    def on_any_event(self, event) -> None:
        """triggered when changes in directory will be detected"""
        if not event.src_path.endswith('alert_json.txt'):
            print('Another file')
            return
        elif event.event_type == 'modified' or event.event_type == 'created':
            print('File has changed')
            while True:
                if Handler.queue:
                    Handler.queue = False
                    self.read_data(event)
                    Handler.queue = True
                    break
                time.sleep(1)
        else:
            print(event.event_type)

    def read_data(self, event) -> None:
        """open file with changes and send it into a model"""
        try:
            with open(event.src_path, encoding='latin-1') as file:
                file.seek(Handler.current_position)
                new_data = file.readlines()
                if new_data:
                    self.save_data(new_data)
                Handler.current_position = file.tell()
        except (PermissionError, FileNotFoundError) as e:
            logger.error(f'{event.src_path} -> {e}')

    @staticmethod
    def save_data(data: list) -> None:
        """Saving events into data base"""
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


if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
