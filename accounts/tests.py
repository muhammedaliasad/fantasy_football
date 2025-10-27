from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from accounts.services import UserRegistrationService
from accounts.models import User
from teams.models import Team
from players.models import Player

User = get_user_model()


class UserRegistrationServiceTests(TestCase):
    """Unit tests for UserRegistrationService"""
    
    def test_create_user_with_team_creates_user(self):
        """Test that user is created with correct attributes"""
        user = UserRegistrationService.create_user_with_team(
            username='testuser',
            email='test@example.com',
            password='Test123456',
            team_name='Test Team'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('Test123456'))
        
    def test_create_user_with_team_creates_team(self):
        """Test that team is created for user"""
        user = UserRegistrationService.create_user_with_team(
            username='testuser',
            email='test@example.com',
            password='Test123456',
            team_name='My Team'
        )
        
        team = Team.objects.get(user=user)
        self.assertIsNotNone(team)
        self.assertEqual(team.name, 'My Team')
        self.assertEqual(float(team.capital), 5000000.00)
        
    def test_create_user_with_team_creates_20_players(self):
        """Test that 20 players are created"""
        user = UserRegistrationService.create_user_with_team(
            username='testuser',
            email='test@example.com',
            password='Test123456',
            team_name='Test Team'
        )
        
        team = Team.objects.get(user=user)
        players = Player.objects.filter(team=team)
        
        self.assertEqual(players.count(), 20)
        self.assertEqual(players.filter(position='GK').count(), 2)
        self.assertEqual(players.filter(position='DF').count(), 5)
        self.assertEqual(players.filter(position='MF').count(), 5)
        self.assertEqual(players.filter(position='AT').count(), 8)
        
    def test_create_user_with_team_creates_players_with_correct_values(self):
        """Test that players have correct initial values"""
        user = UserRegistrationService.create_user_with_team(
            username='testuser',
            email='test@example.com',
            password='Test123456',
            team_name='Test Team'
        )
        
        team = Team.objects.get(user=user)
        players = Player.objects.filter(team=team)
        
        for player in players:
            self.assertEqual(float(player.value), 1000000.00)


class UserSerializerTests(TestCase):
    """Unit tests for user serializers"""
    
    def test_user_registration_serializer_validates_password_match(self):
        """Test password validation"""
        from accounts.serializers import UserRegistrationSerializer
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123456',
            'password_confirm': 'Different',
            'team_name': 'Team'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
    def test_user_registration_serializer_requires_team_name(self):
        """Test that team_name is required"""
        from accounts.serializers import UserRegistrationSerializer
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123456',
            'password_confirm': 'Test123456'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_user_serializer_returns_correct_fields(self):
        """Test user serializer field configuration"""
        from accounts.serializers import UserSerializer
        
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='Pass123'
        )
        
        serializer = UserSerializer(user)
        self.assertIn('id', serializer.data)
        self.assertIn('username', serializer.data)
        self.assertIn('email', serializer.data)


class UserModelTests(TestCase):
    """Unit tests for User model"""
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Pass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Pass123'
        )
        
        self.assertEqual(str(user), 'testuser')
        
    def test_unique_email_constraint(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='Pass123'
        )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='Pass123'
            )

