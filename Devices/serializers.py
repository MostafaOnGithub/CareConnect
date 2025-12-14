from rest_framework import serializers
from .models import Device,UserDeviceLink,SosEvent

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id","serial_number","contacts","sos_event"]

class SosEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SosEvent
        fields = ["id","device","time_stamp"]

    

class UserDeviceLinkSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    class Meta:
        model = UserDeviceLink
        fields = ["user","device","role"]