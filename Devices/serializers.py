from rest_framework import serializers
from .models import Device,UserDeviceLink

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id","serial_number","contacts"]
    

class UserDeviceLinkSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    class Meta:
        model = UserDeviceLink
        fields = ["user","device","role"]