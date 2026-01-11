from django.contrib import admin

from django.contrib import admin
from .models import User
from Devices.models import UserDeviceLink,Device
from Tracking.models import GeoFencing,DangerZone,DeviceLocationLog
from Camera.models import CameraStream
from Alarms.models import Alarm
from Biometrics.models import BiometricReading

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)

models_list = [GeoFencing,DangerZone,DeviceLocationLog,CameraStream,Alarm,BiometricReading,UserDeviceLink]

for model in models_list:
    admin.site.register(model)




