from django.db import models
from rest_framework.generics import get_object_or_404


class Rule(models.Model):
    sid = models.IntegerField()
    gid = models.IntegerField()
    rev = models.IntegerField()
    action = models.CharField(max_length=50)
    message = models.TextField()
    data_json = models.JSONField()

    @staticmethod
    def get_rule(sid: int, rev: int, gid: int) -> 'Rule':
        """Checking for existing of concrete rule"""
        rule = get_object_or_404(Rule, sid=sid, rev=rev, gid=gid)
        return rule
