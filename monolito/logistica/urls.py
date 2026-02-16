from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RotaExtraViewSet

router = DefaultRouter()
router.register(r'rotas-extras', RotaExtraViewSet, basename='rotaextra')

urlpatterns = [
    path('', include(router.urls)),
]
