from rest_framework import serializers
from accounts.serializers import UserSerializer
from players.serializers import PlayerSerializer
from .models import Team


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    user = UserSerializer(read_only=True)
    total_team_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'user', 'name', 'capital', 'total_team_value', 'players', 'created_at')
        read_only_fields = ('capital',)
