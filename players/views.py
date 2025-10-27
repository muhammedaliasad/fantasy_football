from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from teams.models import Team
from .models import Player
from .serializers import PlayerSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Player operations"""
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    
    @action(detail=False, methods=['get'], url_path='my-players')
    def my_players(self, request):
        """Get current user's players"""
        try:
            players = request.user.team.players.all()
            serializer = self.get_serializer(players, many=True)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)
