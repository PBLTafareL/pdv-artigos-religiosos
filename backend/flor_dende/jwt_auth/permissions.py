from rest_framework.permissions import BasePermission

class IsAdminOrFuncionario(BasePermission):
    message = 'Acesso restrito a administradores e funcionários.'
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated: return False
        return request.user.perfil in ['administrador', 'funcionario']

class IsAdministrador(BasePermission):
    message = 'Acesso restrito a administradores.'
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated: return False
        return request.user.perfil == 'administrador'
