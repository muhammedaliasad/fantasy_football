from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from teams.models import Team
from players.models import Player
from transfers.models import TransferListing
from transactions.models import Transaction

User = get_user_model()


class TransferListingTests(TestCase):
    """Test transfer listing functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='seller', email='seller@test.com', password='Pass123')
        self.user2 = User.objects.create_user(username='buyer', email='buyer@test.com', password='Pass123')
        self.team1 = Team.objects.create(user=self.user1, name='Team 1', capital=Decimal('5000000.00'))
        self.team2 = Team.objects.create(user=self.user2, name='Team 2', capital=Decimal('5000000.00'))
        
    def test_list_player_for_sale(self):
        """Test listing a player for sale"""
        player = Player.objects.create(
            team=self.team1,
            name='Test Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        
        self.client.force_authenticate(user=self.user1)
        data = {
            'player_id': player.id,
            'asking_price': '1500000.00'
        }
        response = self.client.post('/api/transfer-listings/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['player']['id'], player.id)
        self.assertEqual(response.data['asking_price'], '1500000.00')
        
    def test_list_other_users_player_fails(self):
        """Test that listing another user's player fails"""
        player = Player.objects.create(
            team=self.team2,
            name='Other Player',
            position='DF',
            value=Decimal('1000000.00')
        )
        
        self.client.force_authenticate(user=self.user1)
        data = {
            'player_id': player.id,
            'asking_price': '1500000.00'
        }
        response = self.client.post('/api/transfer-listings/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_list_already_listed_player_fails(self):
        """Test that listing an already listed player fails"""
        player = Player.objects.create(
            team=self.team1,
            name='Test Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        
        TransferListing.objects.create(player=player, asking_price=Decimal('1500000.00'))
        
        self.client.force_authenticate(user=self.user1)
        data = {
            'player_id': player.id,
            'asking_price': '2000000.00'
        }
        response = self.client.post('/api/transfer-listings/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already listed', response.data['error'])
        
    def test_view_all_active_listings(self):
        """Test viewing all active transfer listings"""
        player = Player.objects.create(
            team=self.team1,
            name='Test Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        TransferListing.objects.create(player=player, asking_price=Decimal('1500000.00'))
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/transfer-listings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_view_my_listings(self):
        """Test viewing only my listings"""
        player = Player.objects.create(
            team=self.team1,
            name='My Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        TransferListing.objects.create(player=player, asking_price=Decimal('1500000.00'))
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/transfer-listings/?my_listings=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['player']['name'], 'My Player')
        
    def test_cancel_my_listing(self):
        """Test canceling own listing"""
        player = Player.objects.create(
            team=self.team1,
            name='Test Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        listing = TransferListing.objects.create(player=player, asking_price=Decimal('1500000.00'))
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/transfer-listings/{listing.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TransferListing.objects.get(id=listing.id).is_active)


class PlayerPurchaseTests(TestCase):
    """Test player purchase functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(username='seller', email='seller@test.com', password='Pass123')
        self.buyer = User.objects.create_user(username='buyer', email='buyer@test.com', password='Pass123')
        self.seller_team = Team.objects.create(user=self.seller, name='Seller Team', capital=Decimal('5000000.00'))
        self.buyer_team = Team.objects.create(user=self.buyer, name='Buyer Team', capital=Decimal('5000000.00'))
        
    def test_buy_player_successfully(self):
        """Test successful player purchase"""
        player = Player.objects.create(
            team=self.seller_team,
            name='Star Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        listing = TransferListing.objects.create(player=player, asking_price=Decimal('2000000.00'))
        
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(f'/api/transfer-listings/{listing.id}/buy/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Player purchased successfully', response.data['message'])
        
        # Check player transfer
        player.refresh_from_db()
        self.assertEqual(player.team, self.buyer_team)
        
        # Check capitals
        self.buyer_team.refresh_from_db()
        self.seller_team.refresh_from_db()
        self.assertEqual(self.buyer_team.capital, Decimal('3000000.00'))
        self.assertEqual(self.seller_team.capital, Decimal('7000000.00'))
        
        # Check listing deactivated
        listing.refresh_from_db()
        self.assertFalse(listing.is_active)
        
        # Check transaction created
        transaction = Transaction.objects.filter(player=player).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.buyer, self.buyer)
        self.assertEqual(transaction.seller, self.seller)
        
    def test_buy_own_player_fails(self):
        """Test that buying own player fails"""
        player = Player.objects.create(
            team=self.seller_team,
            name='My Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        listing = TransferListing.objects.create(player=player, asking_price=Decimal('2000000.00'))
        
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(f'/api/transfer-listings/{listing.id}/buy/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot buy your own player', response.data['error'])
        
    def test_insufficient_capital_fails(self):
        """Test that purchase with insufficient capital fails"""
        self.buyer_team.capital = Decimal('1000000.00')
        self.buyer_team.save()
        
        player = Player.objects.create(
            team=self.seller_team,
            name='Expensive Player',
            position='GK',
            value=Decimal('1000000.00')
        )
        listing = TransferListing.objects.create(player=player, asking_price=Decimal('2000000.00'))
        
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(f'/api/transfer-listings/{listing.id}/buy/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient capital', response.data['error'])
        
    def test_player_value_increases_after_purchase(self):
        """Test that player value increases after purchase"""
        initial_value = Decimal('1000000.00')
        player = Player.objects.create(
            team=self.seller_team,
            name='Test Player',
            position='GK',
            value=initial_value
        )
        listing = TransferListing.objects.create(player=player, asking_price=Decimal('1500000.00'))
        
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(f'/api/transfer-listings/{listing.id}/buy/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        player.refresh_from_db()
        self.assertGreater(player.value, initial_value)
