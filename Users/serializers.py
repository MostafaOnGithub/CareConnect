from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","username","phone","date_joined"]
        read_only_fields = ["id","date_joined"]


class RegestrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email","username","password","phone"]
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            phone=validated_data.get("phone"),
        )