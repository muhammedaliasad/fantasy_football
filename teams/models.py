from django.db import models
from accounts.models import User


class Team(models.Model):
    """Team model representing a user's fantasy team"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team')
    name = models.CharField(max_length=100)
    capital = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_team_value(self):
        """Calculate total value of all players in the team"""
        return sum(player.value for player in self.players.all())

    def __str__(self):
        return f"{self.name} ({self.user.username})"
