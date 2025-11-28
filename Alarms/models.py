from django.db import models
from ..Users.models import User
from ..Devices.models import Device


class Alarm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.TimeField()
    active = models.BooleanField(default=True)

