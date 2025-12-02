    from rest_framework import viewsets
    from .models import Cliente, Entrega, Motorista, Veiculo, Rotas
    from .serializers import EntregaSerializer, MotoristaSerializer, VeiculoSerializer, RotasSerializer, ClienteSerializer
    from django_filterS.rest_framework import DjangoFilterBackend

    class ClienteViewSet(viewsets.ModelViewSet):
        queryset = Cliente.objects.all()
        serializer_class = ClienteSerializer

    class EntregaViewSet(viewsets.ModelViewSet):
        queryset = Entrega.objects.all()
        serializer_class = EntregaSerializer

    class MotoristaViewSet(viewsets.ModelViewSet):
        queryset = Motorista.objects.all()
        serializer_class = MotoristaSerializer

    class VeiculoViewSet(viewsets.ModelViewSet):
        queryset = Veiculo.objects.all()
        serializer_class = VeiculoSerializer

    class RotasViewSet(viewsets.ModelViewSet):
        queryset = Rotas.objects.all()
        serializer_class = RotasSerializer

       '''
        filter_backends = [DjangoFilterBackend]
        filterset_fiels= #[...]
        '''
    
#aseloco