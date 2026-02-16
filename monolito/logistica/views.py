from rest_framework import viewsets
from .models import RotaExtra
from .serializers import RotaExtraSerializer

class RotaExtraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar Rotas Extras e suas paradas.
    """
    queryset = RotaExtra.objects.all().order_by('-data_hora_execucao')
    serializer_class = RotaExtraSerializer
