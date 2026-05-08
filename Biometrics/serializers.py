from rest_framework import serializers
from .models import BiometricReading


class BiometricReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricReading
        fields = ['id', 'device', 'heart_rate', 'timestamp']


class LiveBiometricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricReading
        fields = ['heart_rate', 'timestamp']
