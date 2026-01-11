from rest_framework import serializers
from .models import DeviceLocationLog,GeoFencing,DangerZone
from Devices.models import Device

class DeviceLocationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLocationLog
        fields = ['id', 'device', 'latitude', 'longitude', 'timestamp']

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLocationLog
        fields = ['device','latitude', 'longitude', 'timestamp']

class GeoFencingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoFencing
        fields = [
            'id', 'user', 'device', 'center_lat', 'center_lng',
            'radius', 'active', 'timestamp'
        ]

class DangerZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DangerZone
        fields = [
            'id', 'user', 'device', 'center_lat', 'center_lng',
            'radius', 'active', 'timestamp'
        ]
