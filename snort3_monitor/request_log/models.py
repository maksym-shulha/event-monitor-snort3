from django.db import models


class Request(models.Model):
    user_addr = models.CharField(max_length=50)
    http_method = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=128)
    response = models.IntegerField()
    request_data = models.JSONField()
