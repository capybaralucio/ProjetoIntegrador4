from django.contrib import admin
from .models import (Motorista, Veiculo, Cliente, Rota, Entrega)

admin.site.register(Motorista)
admin.site.register(Veiculo)
admin.site.register(Cliente)
admin.site.register(Rota)
admin.site.register(Entrega)

# Register your models here.
