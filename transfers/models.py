from django.db import models
from players.models import Player


class TransferListing(models.Model):
    """TransferListing model for players listed for sale"""
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='transfer_listing')
    asking_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.name} - ${self.asking_price}"
