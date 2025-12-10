import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import timedelta
from entregas.models import Cliente, Motorista, Veiculo, Rota, Entrega


def converter_tempo(texto):
    if not texto:
        return None

    h, m, s = texto.split(":")

    return timedelta(
        hours=int(h),
        minutes=int(m),
        seconds=int(s),
    )


class Command(BaseCommand):
    help = "Importa automaticamente todos os CSVs da pasta /csv"

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR
        csv_folder = os.path.join(base_dir, "csv")

        print(f"BASE_DIR real: {base_dir}")
        print(f"Lendo arquivos em: {csv_folder}")

        if not os.path.exists(csv_folder):
            print("ERRO: pasta CSV não encontrada")
            return

        order = [
            "clientes.csv",
            "motoristas.csv",
            "veiculos.csv",
            "rotas.csv",
            "entregas.csv",
        ]

        for file_name in order:
            file_path = os.path.join(csv_folder, file_name)

            if not os.path.exists(file_path):
                print(f"Arquivo não encontrado: {file_name}")
                continue

            print(f"\n Importando: {file_name}")

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # ------------------------------
                #  CLIENTES
                # ------------------------------
                if file_name == "clientes.csv":
                    for row in reader:
                        Cliente.objects.update_or_create(
                            cpf_cliente=row["cpf_cliente"],
                            defaults={
                                "nome_cliente": row["nome_cliente"],
                                "endereco": row["endereco"],
                                "cidade": row["cidade"],
                                "estado": row["estado"],
                                "bairro": row["bairro"],
                                "cep": row["cep"],
                                "telefone": row["telefone"],
                                "email": row["email"],
                            }
                        )

                # ------------------------------
                #  MOTORISTAS
                # ------------------------------
                elif file_name == "motoristas.csv":
                    for row in reader:
                        Motorista.objects.update_or_create(
                            cpf=row["cpf"],
                            defaults={
                                "nome_motorista": row["nome_motorista"],
                                "telefone": row["telefone"],
                                "data_cadastro": row["data_cadastro"],
                                "cnh": row["cnh"],
                                "status_motorista": row["status_motorista"],
                            }
                        )

                # ------------------------------
                #  VEÍCULOS
                # ------------------------------
                elif file_name == "veiculos.csv":
                    for row in reader:

                        motorista = None
                        if row["motorista_cpf"]:
                            motorista = Motorista.objects.filter(cpf=row["motorista_cpf"]).first()

                        Veiculo.objects.update_or_create(
                            placa=row["placa"],
                            defaults={
                                "modelo": row["modelo"],
                                "capacidade_maxima": row["capacidade_maxima"],
                                "km_atual": row["km_atual"],
                                "tipo": row["tipo"],
                                "status_veiculo": row["status_veiculo"],
                                "motorista_ativo": motorista,
                            }
                        )

                # ------------------------------
                #  ROTAS
                # ------------------------------
                elif file_name == "rotas.csv":
                    for row in reader:

                        motorista = Motorista.objects.filter(cpf=row["motorista_cpf"]).first()
                        veiculo = Veiculo.objects.filter(placa=row["veiculo_placa"]).first()

                        rota, _ = Rota.objects.update_or_create(
                            id=row["id"],
                            defaults={
                                "nome_rota": row["nome_rota"],
                                "descricao": row["descricao"],
                                "motorista": motorista,
                                "veiculo": veiculo,
                                "data_rota": row["data_rota"],
                                "capacidade_total_utilizada": row["capacidade_total_utilizada"],
                                "km_total_estimado": row["km_total_estimado"],
                                "tempo_estimado": converter_tempo(row["tempo_estimado"]),
                                "status_rota": row["status_rota"],
                            }
                        )

                        # Adiciona clientes (ManyToMany)
                        clientes_ids = row["clientes_cpfs"].split(";")
                        clientes = Cliente.objects.filter(cpf_cliente__in=clientes_ids)
                        rota.clientes.set(clientes)

                # ------------------------------
                #  ENTREGAS
                # ------------------------------
                elif file_name == "entregas.csv":
                    for row in reader:

                        cliente = Cliente.objects.filter(cpf_cliente=row["cliente_cpf"]).first()
                        rota = Rota.objects.filter(id=row["rota_id"]).first()

                        Entrega.objects.update_or_create(
                            codigo_rastreio=row["codigo_rastreio"],
                            defaults={
                                "data_entrega_real": row["data_entrega_real"] or None,
                                "capacidade_necessaria": row["capacidade_necessaria"],
                                "endereco_origem": row["endereco_origem"],
                                "observacoes": row["observacoes"],
                                "endereco_destino": row["endereco_destino"],
                                "valor_frete": row["valor_frete"],
                                "data_entrega_prevista": row["data_entrega_prevista"],
                                "data_solicitacao": row["data_solicitacao"],
                                "cliente": cliente,
                                "rota": rota,
                                "status": row["status"],
                            }
                        )

            print(f"Finalizado: {file_name}")

        print("\nIMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
