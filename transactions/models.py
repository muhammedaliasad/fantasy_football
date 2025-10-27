from django.db import models
from accounts.models import User
from players.models import Player


class Transaction(models.Model):
    """Transaction model to record player transfers"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
        ]

    def __str__(self):
        return f"{self.player.name}: {self.seller.username} -> {self.buyer.username} (${self.transfer_amount})"
