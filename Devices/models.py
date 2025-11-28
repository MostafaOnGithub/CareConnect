from django.db import models
from ..Users.models import User

class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    contacts = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.serial_number
    

class UserDeviceLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    role = models.CharField(max_length=50) 

    def __str__(self):
        return f"{self.user.username} → {self.device.serial_number}"
