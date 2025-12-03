from rest_framework import serializers
from .models import Motorista, Veiculo, Cliente, Rota, Entrega  

class MotoristaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorista
        fields = '__all__'
        
class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        fields = '__all__'  
        
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'  
        
class RotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rota
        fields = '__all__'
    
class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = '__all__'
        
