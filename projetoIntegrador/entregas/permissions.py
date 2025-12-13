#professor não faou sobre isso, mas segundo o chat é necessário para o funcionamento correto das permissões

from rest_framework.permissions import BasePermission #, SAFE_METHODS


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


# class IsOwnerOrReadOnly(BasePermission):
#     """
#     Permissão personalizada para permitir que apenas o proprietário de um objeto
#     possa editá-lo. Outros usuários podem apenas ler (GET, HEAD, OPTIONS).
#     """
#     def has_object_permission(self, request, view, obj):
#         # Permite métodos seguros para qualquer usuário
#         if request.method in SAFE_METHODS:
#             return True
        
#         # Permite edição apenas ao proprietário do objeto
#         return obj.owner == request.user