from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



# ---------- MOTORISTA ----------
class Motorista(models.Model):

    # Tipos de CNH permitidos
    class Cnh(models.TextChoices):
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'
        E = 'E', 'E'

    # Status do motorista
    class Status_motorista(models.TextChoices):
        ATIVO = 'A', 'Motorista ativo'
        INATIVO = 'I', 'Motorista inativo'
        EM_ROTA = 'R', 'Motorista em rota'
        DISPONIVEL = 'D', 'Motorista disponível'


    cpf = models.CharField(max_length=11, primary_key=True)
    nome_motorista = models.CharField(max_length=200, null=False)
    telefone = models.CharField(max_length=15, null=False)
    data_cadastro = models.DateField(null=False)
    cnh = models.CharField(
        max_length=1,
        choices=Cnh.choices,
        default=Cnh.B
    )
    status_motorista = models.CharField(
        max_length=1,
        choices=Status_motorista.choices,
        default=Status_motorista.DISPONIVEL
    )
    # Vínculo com usuário do sistema
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome_motorista



# ---------- VEÍCULO ----------
class Veiculo(models.Model):

    # Tipos de veículo
    class Tipo(models.TextChoices):
        CARRO = '1', 'Carro'
        VAN = '2', 'Van'
        CAMINHAO = '3', 'Caminhão'

    # Status do veículo
    class Status_veiculo(models.TextChoices):
        DISPONIVEL = 'D', 'Disponível'
        EM_USO = 'U', 'Em uso'
        MANUTENCAO = 'M', 'Manutenção'

    placa = models.CharField(max_length=8, primary_key=True)
    modelo = models.CharField(max_length=200, null=False)
    capacidade_maxima = models.PositiveIntegerField( null=False)
    km_atual = models.PositiveIntegerField(null=False)
    motorista_ativo = models.OneToOneField(Motorista, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(
        max_length=1,
        choices=Tipo.choices,
        default=Tipo.CARRO
    )
    status_veiculo = models.CharField(
        max_length=1,
        choices=Status_veiculo.choices,
        default=Status_veiculo.DISPONIVEL
    )

    # Valida compatibilidade entre CNH e tipo de veículo
    def clean(self):
        if self.motorista_ativo:
            cnh = self.motorista_ativo.cnh
            
            compatibilidade = {
                "1": ["B","C","D","E"],
                "2": ["D","E"],
                "3": ["C","E"]
            }

            tipos_validos = compatibilidade.get(self.tipo, [])

            if cnh not in tipos_validos:
                raise ValidationError(
                    f"O motorista {self.motorista_ativo.nome_motorista} possui CNH {cnh}, "
                    f"mas o veículo {self.get_tipo_display()} exige: {', '.join(tipos_validos)}."
                )

    # Garante validação antes de salvar
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.placa



# ---------- CLIENTE ----------
class Cliente(models.Model):
    cpf_cliente = models.CharField(max_length=11, primary_key=True)
    nome_cliente = models.CharField(max_length=200, null=False)
    endereco = models.CharField(max_length=100, null=False)
    cidade = models.CharField(max_length=200, null=False)
    estado = models.CharField(max_length=100, null=False)
    bairro = models.CharField(max_length=200, null=False)
    cep = models.CharField(max_length=8, null=False)
    telefone = models.CharField(max_length=15, null=False)
    email = models.EmailField(max_length=100, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return self.nome_cliente
     


# ---------- ROTA ----------
class Rota(models.Model):

    class Status_rota(models.TextChoices):
        PLANEJADA = 'P', 'Rota a planejar'
        EM_ANDAMENTO = 'A', 'Rota em andamento' 
        CONCLUIDA = 'C', 'Rota concluída'

    clientes = models.ManyToManyField(Cliente)
    nome_rota = models.CharField(max_length=200, null=False)
    descricao = models.CharField(max_length=300, null=False)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, null=False) 
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, null=False)
    data_rota = models.DateField(null=False)
    capacidade_total_utilizada = models.IntegerField(default=0)
    km_total_estimado = models.IntegerField(null=False)
    tempo_estimado = models.DurationField(null=False)
    status_rota = models.CharField(
        max_length=1,
        choices=Status_rota.choices,
        default=Status_rota.PLANEJADA
    )

    def __str__(self):
        return self.nome_rota
    


# ---------- ENTREGA ----------
class Entrega(models.Model):

    class Status_entrega(models.TextChoices):
        PENDENTE = 'P', 'Pendente'
        EM_TRANSITO = 'T', 'Em trânsito'
        ENTREGUE = 'E', 'Entregue'
        CANCELADA = 'C', 'Cancelada'
        REMARCADA = 'R', 'Remarcada'

    codigo_rastreio = models.CharField(max_length=11, primary_key=True)
    data_entrega_real = models.DateField(null=True, blank=True)
    capacidade_necessaria = models.IntegerField(null=False) 
    endereco_origem = models.CharField(max_length=100, null=False)
    observacoes = models.CharField(max_length=300, null=True, blank=True)
    endereco_destino = models.CharField(max_length=100, null=False)
    valor_frete = models.DecimalField(max_digits=5, decimal_places=2)
    data_entrega_prevista = models.DateField(null=False)
    data_solicitacao = models.DateField(null=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True)
    rota = models.ForeignKey(Rota, on_delete=models.SET_NULL, null = True, blank= True)
    status = models.CharField(
         max_length=1,
         choices=Status_entrega.choices,
         default=Status_entrega.PENDENTE
    )


    def __str__(self):
        return self.codigo_rastreio