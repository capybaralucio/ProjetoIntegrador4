import os
import csv
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ValidationError
from entregas.models import Cliente, Motorista, Veiculo, Rota, Entrega


def converter_tempo(texto):
    """Converte string hh:mm:ss em timedelta"""
    if not texto:
        return None
    try:
        h, m, s = map(int, texto.split(":"))
        return timedelta(hours=h, minutes=m, seconds=s)
    except Exception:
        return None


def converter_data(texto):
    """Converte string YYYY-MM-DD em date"""
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except Exception:
        return None


class Command(BaseCommand):
    help = "Importa automaticamente todos os CSVs da pasta /csv"

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR
        csv_folder = os.path.join(base_dir, "csv")

        self.stdout.write(f"BASE_DIR real: {base_dir}")
        self.stdout.write(f"Lendo arquivos em: {csv_folder}")

        if not os.path.exists(csv_folder):
            self.stdout.write("ERRO: pasta CSV não encontrada")
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
                self.stdout.write(f"Arquivo não encontrado: {file_name}")
                continue

            self.stdout.write(f"\nImportando: {file_name}")

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

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

                elif file_name == "motoristas.csv":
                    for row in reader:
                        Motorista.objects.update_or_create(
                            cpf=row["cpf"],
                            defaults={
                                "nome_motorista": row["nome_motorista"],
                                "telefone": row["telefone"],
                                "data_cadastro": converter_data(row["data_cadastro"]),
                                "cnh": row["cnh"],
                                "status_motorista": row["status_motorista"],
                            }
                        )

                elif file_name == "veiculos.csv":
                    for row in reader:
                        motorista = None
                        if row.get("motorista_cpf"):
                            motorista = Motorista.objects.filter(cpf=row["motorista_cpf"]).first()

                        veiculo, created = Veiculo.objects.update_or_create(
                            placa=row["placa"],
                            defaults={
                                "modelo": row["modelo"],
                                "capacidade_maxima": int(row["capacidade_maxima"] or 0),
                                "km_atual": int(row["km_atual"] or 0),
                                "tipo": row["tipo"],
                                "status_veiculo": row["status_veiculo"],
                                "motorista_ativo": motorista,
                            }
                        )

                        # valida compatibilidade CNH
                        try:
                            veiculo.full_clean()
                            veiculo.save()
                        except ValidationError as e:
                            self.stdout.write(f"Erro no veículo {veiculo.placa}: {e}")
                            continue

                elif file_name == "rotas.csv":
                    for row in reader:
                        motorista = Motorista.objects.filter(cpf=row.get("motorista_cpf")).first()
                        veiculo = Veiculo.objects.filter(placa=row.get("veiculo_placa")).first()

                        if not motorista or not veiculo:
                            self.stdout.write(f"Pular rota {row.get('id')}: motorista ou veículo não encontrado")
                            continue

                        rota, _ = Rota.objects.update_or_create(
                            id=row["id"],
                            defaults={
                                "nome_rota": row["nome_rota"],
                                "descricao": row["descricao"],
                                "motorista": motorista,
                                "veiculo": veiculo,
                                "data_rota": converter_data(row["data_rota"]),
                                "capacidade_total_utilizada": int(row.get("capacidade_total_utilizada") or 0),
                                "km_total_estimado": int(row.get("km_total_estimado") or 0),
                                "tempo_estimado": converter_tempo(row.get("tempo_estimado")),
                                "status_rota": row["status_rota"],
                            }
                        )

                        clientes_cpfs = row.get("clientes_cpfs", "")
                        if clientes_cpfs:
                            clientes_ids = clientes_cpfs.split(";")
                            clientes = Cliente.objects.filter(cpf_cliente__in=clientes_ids)
                            rota.clientes.set(clientes)

                elif file_name == "entregas.csv":
                    for row in reader:
                        cliente = Cliente.objects.filter(cpf_cliente=row.get("cliente_cpf")).first()
                        rota = Rota.objects.filter(id=row.get("rota_id")).first() if row.get("rota_id") else None

                        if not cliente:
                            self.stdout.write(f"Pular entrega {row.get('codigo_rastreio')}: cliente não encontrado")
                            continue

                        if row.get("rota_id") and not rota:
                            self.stdout.write(f"Pular entrega {row.get('codigo_rastreio')}: rota não encontrada")
                            continue

                        Entrega.objects.update_or_create(
                            codigo_rastreio=row["codigo_rastreio"],
                            defaults={
                                "data_entrega_real": converter_data(row.get("data_entrega_real")),
                                "capacidade_necessaria": int(row.get("capacidade_necessaria") or 0),
                                "endereco_origem": row["endereco_origem"],
                                "observacoes": row.get("observacoes"),
                                "endereco_destino": row["endereco_destino"],
                                "valor_frete": float(row.get("valor_frete") or 0),
                                "data_entrega_prevista": converter_data(row.get("data_entrega_prevista")),
                                "data_solicitacao": converter_data(row.get("data_solicitacao")),
                                "cliente": cliente,
                                "rota": rota,
                                "status": row["status"],
                            }
                        )

            self.stdout.write(f"Finalizado: {file_name}")

        self.stdout.write("\nIMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
