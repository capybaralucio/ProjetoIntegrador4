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
    
class RotaDashboardSerializer(serializers.ModelSerializer):
    motorista = serializers.SerializerMethodField()
    veiculo = serializers.SerializerMethodField()
    entregas = serializers.SerializerMethodField()
    capacidade_disponivel = serializers.SerializerMethodField()

    class Meta:
        model = Rota
        fields = [
            'id',
            'nome_rota',
            'descricao',
            'motorista',
            'veiculo',
            'entregas',
            'capacidade_total_utilizada',
            'capacidade_disponivel',
            'status_rota',
            'data_rota',
            'km_total_estimado',
            'tempo_estimado'
        ]

    def get_motorista(self, obj):
        if obj.motorista:
            return {
                "cpf": obj.motorista.cpf,
                "nome_motorista": obj.motorista.nome_motorista,
                "telefone": obj.motorista.telefone,
                "status_motorista": obj.motorista.status_motorista,
                "cnh": obj.motorista.cnh
            }
        return None

    def get_veiculo(self, obj):
        if obj.veiculo:
            return {
                "placa": obj.veiculo.placa,
                "modelo": obj.veiculo.modelo,
                "tipo": obj.veiculo.tipo,
                "status_veiculo": obj.veiculo.status_veiculo,
                "capacidade_maxima": obj.veiculo.capacidade_maxima,
                "km_atual": obj.veiculo.km_atual
            }
        return None

    def get_entregas(self, obj):
        entregas = obj.entrega_set.all()
        return [
            {
                "codigo_rastreio": e.codigo_rastreio,
                "cliente": e.cliente.nome_cliente,
                "endereco_origem": e.endereco_origem,
                "endereco_destino": e.endereco_destino,
                "capacidade_necessaria": e.capacidade_necessaria,
                "status": e.status,
                "data_solicitacao": e.data_solicitacao,
                "data_entrega_prevista": e.data_entrega_prevista,
                "data_entrega_real": e.data_entrega_real,
                "valor_frete": e.valor_frete,
                "observacoes": e.observacoes
            }
            for e in entregas
        ]

    def get_capacidade_disponivel(self, obj):
        if obj.veiculo:
            return obj.veiculo.capacidade_maxima - obj.capacidade_total_utilizada
        return None

