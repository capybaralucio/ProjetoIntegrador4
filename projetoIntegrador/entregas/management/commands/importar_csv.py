import csv
from django.core.management.base import BaseCommand
from entregas.models import Motorista, Veiculo, Cliente, Rota, Entrega



class Command(BaseCommand):
    help = 'importa dados do CSV para o banco de dados'

    
    def handle(self, *args, **kwargs):


        #Motorista

        with open('csv/motoristas.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Motorista.objects.get_or_create(
                    cpf=row['cpf'],
                    defaults={
                        'nome_motorista': row['nome_motorista'],
                        'telefone': row['telefone'],
                        'data_cadastro': row['data_cadastro'],
                        'cnh': row['cnh'],
                        'status_motorista': row['status_motorista']
                    }
                )

        self.stdout.write(self.style.SUCESS('Clientes importados'))


        #Veículo

        with open('csv/veiculos.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                motorista = None

                if row['motorista_ativo']:
                    motorista = Motorista.objects.get(cpf=row['motorista_ativo'])

                Veiculo.objects.get_or_create(
                    placa=row['placa'],
                    defaults={
                        'modelo': row['modelo'],
                        'capacidade_maxima': int(row['capacidade_maxima']),
                        'km_atual': int(row['km_atual']),
                        'motorista_ativo':
                        motorista,
                        'tipo': row['tipo'],
                        'status_veiculo': row['status_veiculo']
                    }
                )

        self.stdout.write(self.style.SUCCESS('Veículos importados'))


        #Rota

        with open('csv/rotas.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:

                motorista = Motorista.objects.get(cpf=row['motorista'])
                veiculo = Veiculo.objects.get(placa=row['veiculo'])

                rota, _ = Rota.objects.get_or_create(
                    nome_rota=row['nome_rota'],
                    defaults={
                        'descricao': row['descricao'],
                        'motorista': motorista,
                        'veiculo': veiculo,
                        'data_rota': row['data_rota'],
                        'capacidade_total_utilizada': int(row['capacidade_total_utilizada']),
                        'km_total_estimado': int(row['km_total_estimado']),
                        'tempo_estimado': row['tempo_estimado'],
                        'status_rota': row['status_rota']
                    }
                )

                #Vínculo com clientes (manytomany)
                cpfs_clientes = row['clientes'].split('|')

                for cpf in cpfs_clientes:
                    cliente = Cliente.objects.get(cpf_cliente=cpf)
                    rota.clientes.add(cliente)


        self.stdout.write(self.style.SUCCESS('Rotas importadas'))


        #Entrega

        with open('csv/entregas.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:

                cliente = Cliente.objects.get(cpf_cliente=row['cliente'])
                rota = Rota.objects.get(nome_rota=row['rota'])

                Entrega.objects.get_or_create(
                    codigo_rastreio=row['codigo_rastreio'],
                    defaults={
                        'data_entrega_real': row['data_entrega_real'] or None,
                        'capacidade_necessaria': int(row['capacidade_necessaria']),
                        'endereco_origem': row['endereco_origem'],
                        'observacoes': row['observacoes'],
                        'endereco_destino': row['endereco_destino'],
                        'valor_frete': float(row['valor_frete']),
                        'data_entrega_prevista': row['data_solicitacao'],
                        'cliente': cliente,
                        'rota': rota,
                        'status': row['status']
                    }
                )

        
        self.stdout.write(self.style.SUCCESS('Entregas importadas'))

        self.stdout.write(self.style.SUCCESS('IMPORTAÇÃO COMPLETA'))

        #python manage.py importar_csv