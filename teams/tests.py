from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from teams.models import Team
from players.models import Player

User = get_user_model()


class TeamTests(TestCase):
    """Test team functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123456'
        )
        self.team = Team.objects.create(
            user=self.user,
            name='Test Team',
            capital=Decimal('5000000.00')
        )
        
    def test_get_my_team(self):
        """Test getting current user's team"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/teams/my-team/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Team')
        self.assertEqual(response.data['capital'], '5000000.00')
        
    def test_team_total_value_calculation(self):
        """Test team total value calculation"""
        Player.objects.create(
            team=self.team,
            name='Player 1',
            position='GK',
            value=Decimal('1000000.00')
        )
        Player.objects.create(
            team=self.team,
            name='Player 2',
            position='DF',
            value=Decimal('1500000.00')
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/teams/my-team/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_team_value'], '2500000.00')
        
    def test_team_requires_authentication(self):
        """Test that team endpoint requires authentication"""
        response = self.client.get('/api/teams/my-team/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_team_displays_all_players(self):
        """Test that team shows all players"""
        for i in range(3):
            Player.objects.create(
                team=self.team,
                name=f'Player {i}',
                position='GK',
                value=Decimal('1000000.00')
            )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/teams/my-team/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['players']), 3)
