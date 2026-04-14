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
    # This ensures the API doesn't expect 'user' in the JSON body
    device = serializers.SlugRelatedField(
        slug_field='serial_number', 
        queryset=Device.objects.all()
    )

    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserDeviceLink
        fields = ['id', 'user_name', 'device', 'is_active', 'role']