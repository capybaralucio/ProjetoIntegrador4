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
        
class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = '__all__'
        extra_kwargs = {
            "rota": {"required": False, "allow_null": True}
        }
        
class RotaSerializer(serializers.ModelSerializer):
    # mostra as entregas desta rota (somente leitura)
    entregas = EntregaSerializer(many=True, read_only=True, source='entrega_set')

    class Meta:
        model = Rota
        fields = '__all__'

    # Validação da capacidade total
    def validate(self, data):
        rota = self.instance  # rota sendo atualizada, se existir

        # pega o veículo escolhido
        veiculo = data.get("veiculo") or (rota.veiculo if rota else None)

        if not veiculo:
            return data

        capacidade_max = veiculo.capacidade_maxima

        # soma das entregas
        entregas = Entrega.objects.filter(rota=rota) if rota else []
        capacidade_utilizada = sum(e.capacidade_necessaria for e in entregas)

        nova_capacidade = data.get("capacidade_total_utilizada", capacidade_utilizada)

        if nova_capacidade > capacidade_max: 
            raise serializers.ValidationError({
                "capacidade_total_utilizada": (
                    f"A capacidade total ({nova_capacidade}) excede a capacidade "
                    f"máxima do veículo ({capacidade_max})."
                )
            })

        return data