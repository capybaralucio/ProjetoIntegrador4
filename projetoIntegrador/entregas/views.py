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
<<<<<<< HEAD
    
=======
    #permission_classes = [IsCliente | IsAdmin]
    filter_backends = [DjangoFilterBackend]
    queryset = Cliente.objects.all()
>>>>>>> afe82bd150129fc7af1b7165c3bc04de58929681
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
    filterset_fields = ['codigo_rastreio']
    
    def get_permissions(self):
        if self.request.method == "GET":
            # Qualquer pessoa pode consultar entregas pelo código
            permission_classes = [AllowAny]
        else:
            # POST/PUT/DELETE apenas para usuários logados/admin
            permission_classes = [IsCliente | IsAdmin]
        return [permission() for permission in permission_classes] 
    
    def get_queryset(self):
        # Usuário não logado só consegue buscar por código
        if self.request.method == "GET" and not self.request.user.is_authenticated:
            codigo = self.request.query_params.get("codigo_rastreio", None)
            if codigo:
                return Entrega.objects.filter(codigo_rastreio=codigo)
            return Entrega.objects.none()
        # Usuário logado/admin vê suas entregas normalmente
        user = self.request.user
        if user.is_staff:
            return Entrega.objects.all()
        if hasattr(user, "cliente"):
            return Entrega.objects.filter(cliente=user.cliente)
<<<<<<< HEAD

        return Entrega.objects.none()  
=======
        return Entrega.objects.none() 
    
>>>>>>> afe82bd150129fc7af1b7165c3bc04de58929681
