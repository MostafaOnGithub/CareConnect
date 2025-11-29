from rest_framework import serializers
from .models import CameraStream

class CameraStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraStream
        fields = ['id', 'user', 'device', 'action', 'timestamp']


