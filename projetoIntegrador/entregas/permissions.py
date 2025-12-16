

from rest_framework.permissions import BasePermission

# ============================
# ADMINISTRADOR
# Acesso total ao sistema
# ============================
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

# ============================
# MOTORISTA
# Pode acessar apenas seus dados
# ============================
class IsMotorista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "motorista")


# ============================
# CLIENTE
# Apenas visualização das próprias entregas
# ============================
class IsCliente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "cliente") 

# ============================
# MOTORISTA OU ADMIN
# ============================
class IsMotoristaOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_staff or hasattr(user, "motorista")
            )
        )

# ============================
# CLIENTE OU ADMIN
# ============================
class IsClienteOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_staff or hasattr(user, "cliente")
            )
        )

# ============================
# QUALQUER USUÁRIO AUTENTICADO
# ============================
class IsAnyUser(BasePermission):
#----------------escolhe Admin ou Motorista ou Cliente
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_staff 
                or hasattr(user, "motorista")
                or hasattr(user, "cliente")
            )
        )
