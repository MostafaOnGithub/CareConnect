from django.db import models
from Users.models import User
from django.conf import settings

class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    contacts = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.serial_number
    
class SosEvent(models.Model):
    device = models.ForeignKey(Device,on_delete=models.CASCADE,related_name='sos_event')
    time_stamp = models.DateTimeField(auto_now_add=True)
    

from django.db import models, transaction
from django.contrib.auth.models import User

class UserDeviceLink(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        # If this instance is being saved as active
        if self.is_active:
            # Start a transaction to ensure both updates happen together
            with transaction.atomic():
                # Find all other active links for this user and deactivate them
                UserDeviceLink.objects.filter(
                    user=self.user, 
                    is_active=True
                ).exclude(pk=self.pk).update(is_active=False)
        
        super(UserDeviceLink, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} → {self.device.serial_number} ({'Active' if self.is_active else 'Inactive'})"
