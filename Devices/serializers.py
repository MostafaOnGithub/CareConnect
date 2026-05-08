from rest_framework import serializers
from .models import Device,UserDeviceLink,SosEvent
from Tracking.models import DeviceLocationLog

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id","serial_number","contacts","sos_event"]

class SosEventSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = SosEvent
        fields = ['id', 'time_stamp', 'sos_types', 'location'] # Add other fields as needed

    def get_location(self, obj):
        # Find the location for this device that happened at (or nearest to) the SOS time
        loc = DeviceLocationLog.objects.filter(
            device=obj.device,
            # Adjust this if your location timestamp has a different field name
            timestamp__lte=obj.time_stamp 
        ).order_by('-timestamp').first()

        if loc:
            return {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            }
        return None

    

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