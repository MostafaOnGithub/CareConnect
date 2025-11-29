from django.db import models
from Devices.models import Device

class BiometricReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    heart_rate = models.IntegerField()
    spo2 = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
