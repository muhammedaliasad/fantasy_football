from rest_framework import serializers
from accounts.serializers import UserSerializer
from players.serializers import PlayerSerializer
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'buyer', 'seller', 'player', 'transfer_amount', 'is_active', 'created_at')
        read_only_fields = fields
