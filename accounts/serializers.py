from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .services import UserRegistrationService


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    team_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'team_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        team_name = validated_data.pop('team_name')
        
        user = UserRegistrationService.create_user_with_team(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            team_name=team_name
        )
        
        refresh = RefreshToken.for_user(user)
        user.tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
