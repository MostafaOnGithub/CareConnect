from django.db import models
from..Devices.models import Device
from ..Users.models import User


class DeviceLocationLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']   # very useful for reconstructing route

    def __str__(self):
        return f"{self.device.serial_number} @ {self.latitude}, {self.longitude}"
    

class GeoFencing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    center_lat = models.FloatField()
    center_lng = models.FloatField()
    radius = models.FloatField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class DangerZone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    center_lat = models.FloatField()
    center_lng = models.FloatField()
    radius = models.FloatField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
