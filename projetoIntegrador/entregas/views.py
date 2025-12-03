from rest_framework import viewsets
from .models import Motorista, Veiculo, Cliente, Rota, Entrega
from .serializers import MotoristaSerializer, VeiculoSerializer, ClienteSerializer, RotaSerializer, EntregaSerializer

class MotoristaViewSet(viewsets.ModelViewSet):
    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer  
    
class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer    
    
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
class RotaViewSet(viewsets.ModelViewSet):
    queryset = Rota.objects.all()
    serializer_class = RotaSerializer   
    
class EntregaViewSet(viewsets.ModelViewSet):
    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer    
    
