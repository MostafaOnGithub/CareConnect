from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","username","phone","created_at"]


class RegestrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email","username","password","phone"]
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            phone=validated_data.get('phone')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user