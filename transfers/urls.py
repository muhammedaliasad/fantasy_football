from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransferListingViewSet

router = DefaultRouter()
router.register(r'transfer-listings', TransferListingViewSet, basename='transferlisting')

urlpatterns = [
    path('', include(router.urls)),
]
