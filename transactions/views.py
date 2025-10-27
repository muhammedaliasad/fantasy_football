from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Transaction history"""
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        """Filter transactions based on user"""
        queryset = Transaction.objects.filter(is_active=True)
        
        my_transactions = self.request.query_params.get('my_transactions', None)
        if my_transactions == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(
                buyer=self.request.user) | queryset.filter(seller=self.request.user)
        
        return queryset.order_by('-created_at')
