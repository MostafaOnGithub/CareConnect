from django.db import models
from ..Users.models import User
from..Devices.models import Device

class CameraStream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  
    timestamp = models.DateTimeField(auto_now_add=True)

