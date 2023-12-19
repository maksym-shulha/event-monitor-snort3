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
