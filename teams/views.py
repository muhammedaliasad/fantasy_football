from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Team
from .serializers import TeamSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Team operations"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    @action(detail=False, methods=['get'], url_path='my-team')
    def my_team(self, request):
        """Get current user's team"""
        try:
            team = request.user.team
            serializer = self.get_serializer(team)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)
