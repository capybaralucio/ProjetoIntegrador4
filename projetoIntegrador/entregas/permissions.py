

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
#----------------Usuário admin tem acesso total.
    def has_permission(self, request, view):
        return request.user.is_staff


class IsMotorista(BasePermission):
#----------------Motorista só pode ver suas rotas/entregas.
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "motorista")


class IsCliente(BasePermission):
#----------------Cliente só pode ver suas entregas.
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "cliente") 

class IsMotoristaOrAdmin(BasePermission):
#----------------Diferenciacão do Motorista pro Admin.
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_staff or hasattr(user, "motorista")
            )
        )

class IsClienteOrAdmin(BasePermission):
#----------------Diferenciacão do Cliente pro Admin.
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_staff or hasattr(user, "cliente")
            )
        )

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
