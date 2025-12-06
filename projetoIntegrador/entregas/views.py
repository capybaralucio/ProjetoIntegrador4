from rest_framework import viewsets, permissions
from .models import Motorista, Veiculo, Cliente, Rota, Entrega
from .serializers import MotoristaSerializer, VeiculoSerializer, ClienteSerializer, RotaSerializer, EntregaSerializer
from .permissions import IsAdmin, IsMotorista, IsCliente
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny

class MotoristaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsMotorista | IsAdmin]
    
    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer  
    
    def get_queryset(self): # restringe o acesso conforme o usuário
        user = self.request.user

        if user.is_staff:
            return Motorista.objects.all()

        if hasattr(user, "motorista"):
            # motorista só vê ele mesmo
            return Motorista.objects.filter(cpf=user.motorista.cpf)

        return Motorista.objects.none()
    
class VeiculoViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsMotorista | IsAdmin]
    
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status_veiculo", "tipo"]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Veiculo.objects.all()

        if hasattr(user, "motorista"):
            return Veiculo.objects.filter(motorista_ativo=user.motorista)

        return Veiculo.objects.none()   
    
class ClienteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsCliente | IsAdmin]
    
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            # Permitir acesso público para requisições GET (pesquisa/filtros)
            permission_classes = [AllowAny]
        else:
            # Para POST, PUT, DELETE, aplicar permissão customizada
            permission_classes = [IsCliente | IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self): # restringe o acesso conforme o usuário
        user = self.request.user

        if user.is_staff:
            return Cliente.objects.all()

        if hasattr(user, "cliente"):
            # cliente só vê ele mesmo
            return Cliente.objects.filter(cpf_cliente=user.cliente.cpf_cliente)

        return Cliente.objects.none()
    
class RotaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin | IsMotorista]
    
    queryset = Rota.objects.all()
    serializer_class = RotaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["veiculo", "status_rota"]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Rota.objects.all()

        if hasattr(user, "motorista"):
            return Rota.objects.filter(veiculo__motorista_ativo=user.motorista)

        return Rota.objects.none()
    
class EntregaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin | IsMotorista | IsCliente]
    
    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer  
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "rota"]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Entrega.objects.all()

        if hasattr(user, "motorista"):
            return Entrega.objects.filter(rota__motorista=user.motorista)

        if hasattr(user, "cliente"):
            return Entrega.objects.filter(cliente=user.cliente)

        return Entrega.objects.none()  
    
