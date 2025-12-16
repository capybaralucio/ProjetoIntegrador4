# 📦 Projeto Integrador – API de Logística e Entregas

---------------------------
## 1. Descrição Geral do Projeto

Este projeto consiste no desenvolvimento de uma **API REST** para gerenciamento de um sistema de logística e entregas,
utilizando **Django** e **Django Rest Framework (DRF)**. A API permite o cadastro e gerenciamento de 
**motoristas, veículos, clientes, rotas e entregas**, com controle de autenticação e permissões por perfil de usuário.

---------------------------
## 2. Tecnologias Utilizadas

* Python 3.x
* Django 5.2
* Django Rest Framework
* SQLite3
* Token Authentication
* Swagger / OpenAPI (drf-spectacular)

---------------------------
## 3. Estrutura de Pastas do Projeto

```text
projetoIntegrador/
│── MeuAmbiente/
│── projetoIntegrador/
│   ├── csv
│   │   ├── clientes.csv
│   │   ├── entregas.csv
│   │   ├── motoristas.csv
│   │   ├──rotas.csv
│   │   ├──veiculos.csv
│ 
│   ├── entregas/
│   │   │   ├──management
│   │   │   │   ├── commands
│   │   │   │   │   ├── importar>csv.py 
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── auth_views.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── views.py
│ 
│   ├── projetoIntegrador/
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│
│── db.sqlite3
│── manage.py
│── requirements.txt
│── request.txt
```

---------------------------
## 4. Instalação e Execução do Projeto

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---------------------------
## 5. Autenticação e Segurança

A API utiliza **Token Authentication**, garantindo que apenas usuários autenticados 
possam acessar determinados endpoints.

### Obtenção do Token

📌 **URL:**

```
http://127.0.0.1:8000/api/token/
```

Envie usuário e senha cadastrados para receber o token.

```json
{
  "username": "admin",
  "password": "123456"
}
```

---------------------------
## 6. Documentação da API – Swagger (OpenAPI)

A documentação interativa da API é acessada via Swagger.

### 🔗 Links Importantes (para uso durante a apresentação)

* 📘 **Swagger UI** (documentação interativa):
  👉 [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

* 📕 **ReDoc** (documentação alternativa):
  👉 [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

### 🔐 Autorização no Swagger

No canto superior direito do Swagger, clique em **Authorize** e informe:

```
Token SEU_TOKEN_AQUI
```

---------------------------
## 7. Endpoints

### 📍 Listagem de Rotas

```
GET http://127.0.0.1:8000/rotas/
```

📂 Caminho do código:

```
entregas/views.py → class RotaViewSet
```

```python
class RotaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsClienteOrAdmin]
```

---------------------------
### 📍 Detalhamento de Rota

```
GET http://127.0.0.1:8000/rotas/1/dashboard/
```

📂 Caminho do código:

```
entregas/views.py → função rota_dashboard
```

```python
@api_view(['GET'])
def rota_dashboard(request, pk):
    rota = Rota.objects.get(pk=pk)
```

---

## 8. Modelagem do Banco de Dados

### 📐 Diagrama – BrModelo
<img width="1429" height="826" alt="brmodelo4" src="https://github.com/user-attachments/assets/b4e0b170-faeb-4bfa-94a3-f8ebb0d27f65" />



### 📐 Diagrama – SQL Power Architect

![sqlpower4](https://github.com/user-attachments/assets/19a84042-669c-4603-b1b8-7dd07e92a13b)


---------------------------
## 9. Tabela de Relacionamentos do Sistema

| Entidade Origem | Relacionamento | Entidade Destino |
| --------------- | -------------- | ---------------- |
| Motorista       | 1 : 1          | Veículo          |
| Cliente         | 1 : N          | Entrega          |
| Rota            | 1 : N          | Entrega          |
| Cliente         | N : N          | Rota             |
| Motorista       | 1 : N          | Rota             |


---------------------------
## 10. Modelos Django (Trechos para Print)

### 📂 entregas/models.py

```python
class Rota(models.Model):
    clientes = models.ManyToManyField(Cliente)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
```


