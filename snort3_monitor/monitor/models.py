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


class Rule(models.Model):
    sid = models.IntegerField()
    rev = models.IntegerField()
    gid = models.IntegerField()
    action = models.CharField(max_length=50)
    message = models.TextField()
    data_json = models.JSONField()

    @staticmethod
    def get_rule(sid: int, rev: int, gid: int) -> 'Rule':
        """Checking for existing of concrete rule"""
        rule = get_object_or_404(Rule, sid=sid, rev=rev, gid=gid)
        return rule


class Request(models.Model):
    user_addr = models.CharField(max_length=50)
    http_method = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=128)
    response = models.IntegerField()
    request_data = models.JSONField()
