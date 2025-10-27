from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'name', 'position', 'position_display', 'value', 'team', 'team_name')
        read_only_fields = ('value', 'team')
