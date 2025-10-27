from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'register':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """User registration endpoint"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'tokens': user.tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='profile')
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
