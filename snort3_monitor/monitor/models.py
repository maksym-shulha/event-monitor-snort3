from django.db import models
from rule.models import Rule


class Event(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    src_addr = models.CharField(max_length=128)
    src_port = models.IntegerField(null=True, blank=True)
    dst_addr = models.CharField(max_length=128)
    dst_port = models.IntegerField(null=True, blank=True)
    proto = models.CharField(max_length=128)
    mark_as_deleted = models.BooleanField(default=False)


class Request(models.Model):
    user_addr = models.CharField(max_length=50)
    http_method = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=128)
    response = models.IntegerField()
    request_data = models.JSONField()
