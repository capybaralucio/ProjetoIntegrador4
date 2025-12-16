from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser,IsAuthenticatedOrReadOnly, IsAuthenticated
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
    permission_classes = [] #será definido no get_permissions

    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer  


    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]#usuários autenticados podem ver motoristas
        return [permission() for permission in permission_classes]
    

    def get_queryset(self): # restringe o acesso conforme o usuário
        user = self.request.user


        if user.is_staff:
            return Motorista.objects.all()

        if hasattr(user, "motorista"):
            # motorista só vê ele mesmo
            return Motorista.objects.filter(cpf=user.motorista.cpf)

        return Motorista.objects.none()



# ------------------- ação: ATRIBUIR UM VEÍCULO A UM MOTORISTA ----------------------
@action(detail=True, methods=["put"], url_path="atribuir-veiculo")
def atribuir_veiculo(self, request, pk=None):
    """
    Atribui um veículo disponível a este motorista.
    Atualiza o motorista_ativo no veículo e muda status para 'em_uso'.
    """
    motorista = self.get_object()
    placa = request.data.get("placa")  # só envia a placa do veículo

    if not placa:
        return Response({"erro": "O campo 'placa' é obrigatório."}, status=400)

    try:
        veiculo = Veiculo.objects.get(placa=placa, status_veiculo="disponível")
        veiculo.motorista_ativo = motorista
        veiculo.status_veiculo = "em_uso"
        veiculo.save()
        return Response({"status": f"Veículo {placa} atribuído ao motorista {motorista.nome_motorista}."})
    except Veiculo.DoesNotExist:
        return Response({"erro": "Veículo não disponível."}, status=400)



# ------------------- ação: LIBERAR O VEÍCULO DO MOTORISTA ----------------------
@action(detail=True, methods=["put"], url_path="liberar-veiculo")
def liberar_veiculo(self, request, pk=None):
    """
    Libera o veículo atualmente vinculado ao motorista.
    Marca o veículo como disponível e remove o vínculo com o motorista.
    """
    motorista = self.get_object()
    try:
        veiculo = Veiculo.objects.get(motorista_ativo=motorista)
        veiculo.motorista_ativo = None
        veiculo.status_veiculo = "disponível"
        veiculo.save()
        return Response({"status": f"Veículo {veiculo.placa} liberado do motorista {motorista.nome_motorista}."})
    except Veiculo.DoesNotExist:
        return Response({"erro": "Nenhum veículo vinculado a este motorista."}, status=400)
    


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



# ------------------- ação: LISTA TODOS OS VEÍCULOS DISPONÍVEIS ----------------------
    @action(detail=False, methods=["get"], url_path="disponiveis")
    def veiculos_disponiveis(self, request):
        veiculos = Veiculo.objects.filter(status_veiculo="D", motorista_ativo=None)
        serializer = self.get_serializer(veiculos, many=True)
        return Response(serializer.data)





# ------------------- CLIENTE ------------------------
class ClienteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    

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
    permission_classes = [IsAuthenticated]
    
    queryset = Rota.objects.all()
    serializer_class = RotaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["veiculo", "status_rota"]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Rota.objects.all()

        if hasattr(user, "cliente"):
            return Rota.objects.filter(clientes=user.cliente)

        return Rota.objects.none()
    
 # ------------------- ação: LISTAR ENTREGAS DA ROTA ---------------------- 
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def entregas(self, request, pk=None):
        rota = self.get_object()
        entregas = rota.entrega_set.all()
        serializer = EntregaSerializer(entregas, many=True)
        return Response(serializer.data)
    
 # ------------------- ação: ADICIONAR ENTREGAS À ROTA ----------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def adicionar_entrega(self, request, pk=None):
        rota = self.get_object()


        if rota.status_rota != "P":
            return Response(
                {"erro": "Só é possível adicionar entregas em rotas planejadas"},
                status=400
            )


        entrega_id = request.data.get("entrega_id")

        if not entrega_id:
            return Response({"erro": "entrega_id é obrigatório"}, status=400)
        
        try:
            entrega = Entrega.objects.get(id=entrega_id)
        except Entrega.DoesNotExist:
            return Response({"erro": "Entrega não encontrada"}, status=404)
        
        if entrega.rota:
            return Response({"erro": "Entrega já está vinculada a uma rota"}, status=400)
        
        nova_capacidade = (
            rota.capacidade_total_utilizada + entrega.capacidade_necessaria
        )

        if nova_capacidade > rota.veiculo.capacidade_maxima:
            return Response(
                {"erro": "Capacidade do veículo excedida"}, status=400
            )
        
        entrega.rota = rota
        entrega.save()

        rota.capacidade_total_utilizada = nova_capacidade
        rota.save()

        return Response({"mensagem": "Entrega adicionada à rota com sucesso!"})
    
 # ------------------- ação: REMOVER ENTREGA DA ROTA ----------------------
    @action(detail=True, methods=["delete"], url_path="entregas/(?P<entrega_id>[^/.]+)", permission_classes=[IsAdmin],)
    def remover_entrega(self, request, pk=None, entrega_id=None):
        rota = self.get_object()

        try:
            entrega = Entrega.objects.get(id=entrega_id, rota=rota)
        except Entrega.DoesNotExist:
            return Response({"erro": "Entrega não encontrada nesta rota"}, status=404)
        
        rota.capacidade_total_utilizada = max(
            0,
            rota.capacidade_total_utilizada - entrega.capacidade_necessaria
        )
        rota.save()

        entrega.rota = None
        entrega.save()

        return Response({"mensagem": "Entrega removida da rota"})
    
 # ------------------- ação: CAPACIDADE DA ROTA ----------------------
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def capacidade(self, request, pk=None):
        rota = self.get_object()

        return Response({
            "capacidade_maxima_veiculo": rota.veiculo.capacidade_maxima,
            "capacidade_utilizada": rota.capacidade_total_utilizada,
            "capacidade_disponivel": (
                rota.veiculo.capacidade_maxima - rota.capacidade_total_utilizada
            )
        })
        


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

        user = self.request.user


        # Usuário não logado só consegue buscar por código
        if self.request.method == "GET" and not user.is_authenticated:
            codigo = self.request.query_params.get("codigo_rastreio", None)
            if codigo:
                return Entrega.objects.filter(codigo_rastreio=codigo)
            return Entrega.objects.none()
        # Usuário logado/admin vê suas entregas normalmente

        if user.is_staff:
            return Entrega.objects.all()
        if hasattr(user, "cliente"):
            return Entrega.objects.filter(cliente=user.cliente)
        if hasattr(user, "motorista"):
            return Entrega.objects.filter(motorista=user.motorista)

        return Entrega.objects.none()
    
    
    def update(self, request, *args, **kwargs):
        '''
        validar quem pode atualizar a entrega:
        ADMIN: atualiza qualquer entrega
        MOTORISTA: só pode atualizar as próprias entregas
        CLIENTE OR OTHER: não consegue atualizar
        '''

        entrega = self.get_object()
        user = request.user

        if user.is_staff:
            return super().update(request, *args, **kwargs)
        
        if hasattr(user, "motorista") and entrega.motorista == user.motorista:
            return super().update(request, *args, **kwargs)
        
        return Response(
            {"erro": "Você não tem permissão para alterar esta entrega."}, status=403
        )
    

    def partial_update(self, request, *args, **kwargs):
        '''
        a mesma validação do update(), porém para atualizações parcias (PATCH)
        '''

        return self.update(request, *args, **kwargs)
    


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



