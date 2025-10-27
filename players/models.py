from django.db import models
from teams.models import Team


class Player(models.Model):
    """Player model representing a player in the game"""
    
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('AT', 'Attacker'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_position_display()}) - {self.team.name}"
