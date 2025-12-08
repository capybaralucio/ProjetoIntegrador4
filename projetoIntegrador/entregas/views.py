from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from .models import Motorista, Veiculo, Cliente, Rota, Entrega
from .serializers import (
    MotoristaSerializer, VeiculoSerializer, ClienteSerializer,
    RotaSerializer, EntregaSerializer
)
from .permissions import IsAdmin, IsMotorista, IsCliente

# ------------------- MOTORISTA ------------------------
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
    
# ------------------- VEICULO ------------------------
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
    
# ------------------- ação: VINCULAR MOTORISTA ----------------------
@action(detal=True, methods=["post"], permission_classes=[IsAdmin])    
def vincular_motorista(self, request, pk=None):
    veiculo = self.get_object()
    motoristas_cpf = request.data.get("motorista_cpf")

    if not motorista_cpf:
        return Response({"erro": "motorista_cpf é obrigatório"}, status=400)

    try: 
        motorista = Motorista.objects.get(cpf=motorista_cpf)
    except Motorista.DoesNotExist:
        return Response ({"erro": "Motorista não encontrado"}, status=404)

    veiculo.motorista_ativo = motorista
    veiculo.save()

    return Response({"mensagem": "Motorista vinculado com sucesso!"})


# ------------------- CLIENTE ------------------------
class ClienteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permission.IsAuthenticated()]
        return [IsCliente() | IsAdmin()]
    
    def get_queryset(self): # restringe o acesso conforme o usuário
        user = self.request.user

        if user.is_staff:
            return Cliente.objects.all()

        if hasattr(user, "cliente"):
            # cliente só vê ele mesmo
            return Cliente.objects.filter(cpf_cliente=user.cliente.cpf_cliente)

        return Cliente.objects.none()
    
# ------------------- ROTA ------------------------
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
            return Rota.objects.filter(motorista=user.motorista)

        return Rota.objects.none()
    
# ------------------- ENTREGA ------------------------
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
