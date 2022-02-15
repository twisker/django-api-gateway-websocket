from django.db import models

# Create your models here.


class WebSocketOnlineDevice(models.Model):
    provider_id = models.IntegerField()
    device_id = models.CharField(max_length=64)
    user_id = models.CharField(max_length=64)
    registered_datetime = models.DateTimeField(auto_now_add=True)
    last_active_datetime = models.DateTimeField(auto_now=True)
