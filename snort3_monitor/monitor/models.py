import json
from datetime import datetime

from django.db import models
from django.shortcuts import get_object_or_404


class Event(models.Model):
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    src_addr = models.CharField(max_length=128)
    src_port = models.IntegerField(null=True, blank=True)
    dst_addr = models.CharField(max_length=128)
    dst_port = models.IntegerField(null=True, blank=True)
    proto = models.CharField(max_length=128)
    mark_as_deleted = models.BooleanField(default=False)

    @staticmethod
    def create_from_watcher(data: list) -> None:
        """method for processing data from watcher script"""
        for line in data:
            try:
                event_data = json.loads(line)

                allowed_fields = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'proto', 'seconds', 'sid', 'rev']
                event_data = {key: value for key, value in event_data.items() if key in allowed_fields}
                timestamp = datetime.fromtimestamp(event_data.pop('seconds'))
                rule = Rule.get_by_sid_and_rev(event_data.pop('sid'), event_data.pop('rev'))

                new_event = Event(**event_data)
                new_event.rule = rule
                new_event.timestamp = timestamp
                new_event.save()
            except KeyError as e:
                print(e)


class Rule(models.Model):
    sid = models.IntegerField()
    rev = models.IntegerField(default=1)
    action = models.CharField(max_length=20)
    message = models.TextField()
    data_json = models.JSONField()

    @staticmethod
    def get_by_sid_and_rev(sid: int, rev: int) -> 'Rule':
        """Checking for existing of concrete rule"""
        rule = get_object_or_404(Rule, sid=sid, rev=rev)
        return rule
