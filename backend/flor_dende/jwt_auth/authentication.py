from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError):
            raise AuthenticationFailed('Token inválido ou expirado. Faça login novamente.')
