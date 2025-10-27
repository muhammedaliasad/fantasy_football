from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction as db_transaction
from decimal import Decimal
import random

from players.models import Player
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from .models import TransferListing
from .serializers import TransferListingSerializer


class TransferListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Transfer Listing operations"""
    serializer_class = TransferListingSerializer
    
    def get_queryset(self):
        """Filter queryset based on user and active status"""
        queryset = TransferListing.objects.filter(is_active=True)
        
        my_listings = self.request.query_params.get('my_listings', None)
        if my_listings == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(player__team__user=self.request.user)
        
        return queryset
    
    def create(self, request):
        """Create a new transfer listing"""
        player_id = request.data.get('player_id')
        
        try:
            player = Player.objects.get(id=player_id, team__user=request.user)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player not found or does not belong to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if TransferListing.objects.filter(player=player, is_active=True).exists():
            return Response(
                {'error': 'Player is already listed for transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asking_price = request.data.get('asking_price')
        listing = TransferListing.objects.create(
            player=player,
            asking_price=asking_price
        )
        
        serializer = self.get_serializer(listing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Buy a player from transfer listing"""
        listing = self.get_object()
        
        if listing.player.team.user == request.user:
            return Response(
                {'error': 'You cannot buy your own player'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with db_transaction.atomic():
            buyer_team = request.user.team
            seller_team = listing.player.team
            
            if buyer_team.capital < listing.asking_price:
                return Response(
                    {'error': 'Insufficient capital'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            asking_price = Decimal(str(listing.asking_price))
            buyer_team.capital = Decimal(str(buyer_team.capital)) - asking_price
            seller_team.capital = Decimal(str(seller_team.capital)) + asking_price
            
            buyer_team.save()
            seller_team.save()
            
            seller_user = listing.player.team.user
            
            listing.player.team = buyer_team
            
            value_increase = Decimal(str(random.uniform(0.05, 0.15)))
            listing.player.value = Decimal(str(listing.player.value)) * (Decimal('1') + value_increase)
            listing.player.save()
            
            transaction = Transaction.objects.create(
                buyer=request.user,
                seller=seller_user,
                player=listing.player,
                transfer_amount=listing.asking_price,
                is_active=True
            )
            
            listing.is_active = False
            listing.save()
        
        return Response({
            'message': 'Player purchased successfully',
            'transaction': TransactionSerializer(transaction).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a transfer listing"""
        listing = self.get_object()
        
        if listing.player.team.user != request.user:
            return Response(
                {'error': 'You can only cancel your own listings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        listing.is_active = False
        listing.save()
        
        return Response({'message': 'Transfer listing cancelled'}, status=status.HTTP_200_OK)
