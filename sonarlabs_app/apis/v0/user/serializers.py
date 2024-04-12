from rest_framework import serializers
from sonarlabs_app.models import User

class RegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        

class LoginUserSerializer(serializers.Serializer):

    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
