from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from teams.models import Team
from players.models import Player
from transactions.models import Transaction

User = get_user_model()


class TransactionTests(TestCase):
    """Test transaction history functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='Pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='Pass123')
        self.team1 = Team.objects.create(user=self.user1, name='Team 1', capital=Decimal('5000000.00'))
        self.team2 = Team.objects.create(user=self.user2, name='Team 2', capital=Decimal('5000000.00'))
        
    def test_view_all_transactions(self):
        """Test viewing all transactions"""
        player = Player.objects.create(
            team=self.team1,
            name='Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        
        Transaction.objects.create(
            buyer=self.user2,
            seller=self.user1,
            player=player,
            transfer_amount=Decimal('1500000.00')
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_view_my_transactions(self):
        """Test viewing only my transactions"""
        player = Player.objects.create(
            team=self.team1,
            name='Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        
        Transaction.objects.create(
            buyer=self.user2,
            seller=self.user1,
            player=player,
            transfer_amount=Decimal('1500000.00')
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/transactions/?my_transactions=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['seller']['username'], 'user1')
        
    def test_transactions_filtered_by_active(self):
        """Test that only active transactions are shown"""
        player = Player.objects.create(
            team=self.team1,
            name='Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        
        Transaction.objects.create(
            buyer=self.user2,
            seller=self.user1,
            player=player,
            transfer_amount=Decimal('1500000.00'),
            is_active=True
        )
        Transaction.objects.create(
            buyer=self.user2,
            seller=self.user1,
            player=player,
            transfer_amount=Decimal('1500000.00'),
            is_active=False
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_transactions_require_authentication(self):
        """Test that transactions endpoint requires authentication"""
        response = self.client.get('/api/transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
