from decimal import Decimal
import random
import string
from accounts.models import User
from teams.models import Team
from players.models import Player


class UserRegistrationService:
    """Service for handling user registration with team creation"""
    
    @staticmethod
    def create_user_with_team(username, email, password, team_name):
        """Create a user with a team and 20 players"""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        team = Team.objects.create(
            user=user,
            name=team_name,
            capital=Decimal('5000000.00')
        )
        
        position_counts = {
            'GK': 2,
            'DF': 5,
            'MF': 5,
            'AT': 8,
        }
        
        for position, count in position_counts.items():
            for i in range(count):
                player_name = f"Player_{position}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
                
                Player.objects.create(
                    team=team,
                    name=player_name,
                    position=position,
                    value=Decimal('1000000.00')
                )
        
        return user
