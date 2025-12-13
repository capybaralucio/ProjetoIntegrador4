from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import Motorista, Veiculo, Cliente, Rota, Entrega
from .serializers import (
    MotoristaSerializer, VeiculoSerializer, ClienteSerializer,
    RotaSerializer, EntregaSerializer, RotaDashboardSerializer
)
from .permissions import (
    IsAdmin, IsMotorista, IsCliente, 
    IsMotoristaOrAdmin, IsClienteOrAdmin, IsAnyUser
)
# ------------------- MOTORISTA ------------------------
class MotoristaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsMotoristaOrAdmin]
    
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
    permission_classes = [IsMotoristaOrAdmin]
    
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
    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])    
    def vincular_motorista(self, request, pk=None):
        veiculo = self.get_object()
        motorista_cpf = request.data.get("cpf")

        if not motorista_cpf:
            return Response({"erro": "CPF do motorista é obrigatório"}, status=400)

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
    filter_backends = [DjangoFilterBackend]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsMotoristaOrAdmin()]
    
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
    permission_classes = [IsClienteOrAdmin]
    
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
    permission_classes = [IsAnyUser] 
    
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
            permission_classes = [IsClienteOrAdmin]
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

        return Entrega.objects.none()  
    

@api_view(['GET'])
def rota_dashboard(request, pk):
    try:
        rota = Rota.objects.get(pk=pk)
    except Rota.DoesNotExist:
        return Response({"error": "Rota não encontrada"}, status=404)

    # Serializa a rota básica (motorista, veículo)
    serializer = RotaDashboardSerializer(rota)
    data = serializer.data

    # Calcula capacidade utilizada e disponível
    entregas = rota.entrega_set.select_related('cliente').all()
    capacidade_utilizada = sum(e.capacidade_necessaria for e in entregas)
    capacidade_disponivel = rota.veiculo.capacidade_maxima - capacidade_utilizada

    # Monta lista de entregas detalhadas
    entregas_detalhadas = []
    for e in entregas:
        entregas_detalhadas.append({
            "codigo_rastreio": e.codigo_rastreio,
            "status": e.status,
            "capacidade_necessaria": e.capacidade_necessaria,
            "endereco_origem": e.endereco_origem,
            "endereco_destino": e.endereco_destino,
            "data_entrega_prevista": e.data_entrega_prevista,
            "data_entrega_real": e.data_entrega_real,
            "cliente": {
                "cpf": e.cliente.cpf_cliente,
                "nome": e.cliente.nome_cliente,
                "endereco": e.cliente.endereco,
                "cidade": e.cliente.cidade,
                "estado": e.cliente.estado,
                "bairro": e.cliente.bairro,
                "cep": e.cliente.cep,
                "telefone": e.cliente.telefone,
                "email": e.cliente.email,
            },
            "observacoes": e.observacoes,
            "valor_frete": e.valor_frete,
        })

    # Adiciona campos extras ao retorno
    data['capacidade_total_utilizada'] = capacidade_utilizada
    data['capacidade_disponivel'] = capacidade_disponivel
    data['entregas'] = entregas_detalhadas

    return Response(data)



