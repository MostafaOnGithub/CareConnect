from django.contrib import admin
from .models import Device,UserDeviceLink

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'contacts',]


class UserDeviceLinkInline(admin.TabularInline):
    model = UserDeviceLink
    extra = 0  # Don’t auto-create any blank rows
