from rest_framework import serializers
from players.serializers import PlayerSerializer
from .models import TransferListing


class TransferListingSerializer(serializers.ModelSerializer):
    """Serializer for TransferListing model"""
    player = PlayerSerializer(read_only=True)
    player_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TransferListing
        fields = ('id', 'player', 'player_id', 'asking_price', 'is_active', 'created_at')
        read_only_fields = ('is_active',)
