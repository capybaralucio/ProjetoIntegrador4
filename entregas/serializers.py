from rest_framework import serializers
from .models import Cliente, Entrega, Motorista, Veiculo, Rotas

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class EntregaSerializer(serializers.ModelSerializers):
    class Meta:
        model = Entrega
        fields = '__all__' 

class MotoristaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorista
        fields = '__all__'

class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        fields = '__all__'

class RotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rotas
        fields = '__all__'

#seloco