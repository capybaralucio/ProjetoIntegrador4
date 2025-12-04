from django.db import models
from django.contrib.auth.models import User


class Motorista(models.Model):

    class Cnh(models.TextChoices):
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'
        E = 'E', 'E'

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome_motorista



class Veiculo(models.Model):

    class Tipo(models.TextChoices):
        CARRO = '1', 'Carro'
        VAN = '2', 'Van'
        CAMINHAO = '3', 'Caminhão'

    class Status_veiculo(models.TextChoices):
        DISPONIVEL = 'D', 'Disponível'
        EM_USO = 'U', 'Em uso'
        MANUTENCAO = 'M', 'Manutenção'

    placa = models.CharField(max_length=8, primary_key=True)
    modelo = models.CharField(max_length=200, null=False)
    capacidade_maxima = models.IntegerField( null=False)
    km_atual = models.IntegerField(null=False)
    motorista_ativo = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True, unique=True)
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

    def __str__(self):
        return self.placa


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
    rota = models.ForeignKey(Rota, on_delete=models.CASCADE)
    status = models.CharField(
         max_length=1,
         choices=Status_entrega.choices,
         default=Status_entrega.PENDENTE
    )


    def __str__(self):
        return self.codigo_rastreio