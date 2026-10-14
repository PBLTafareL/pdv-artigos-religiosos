import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.accounts.models import User
from apps.accounts.serializers import (
    LoginSerializer, UserListSerializer, UserDetailSerializer,
    UserCreateSerializer, UserUpdateSerializer,
    ClienteListSerializer, ClienteDetailSerializer,
    ClienteCreateSerializer, ClienteUpdateSerializer,
)
from apps.core.choices import PerfilUsuario
from apps.core.pagination import StandardPagination
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario, IsAdministrador

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = LoginSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        user   = s.validated_data['user']
        tokens = s.get_tokens(user)
        return Response({
            'access': tokens['access'], 'refresh': tokens['refresh'],
            'usuario': {'id': user.id, 'nome': user.nome, 'email': user.email,
                        'username': user.username, 'perfil': user.perfil,
                        'perfil_display': user.get_perfil_display()}
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            token = request.data.get('refresh')
            if token: RefreshToken(token).blacklist()
        except TokenError: pass
        return Response({'mensagem': 'Logout realizado.'})

class MeuPerfilView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserDetailSerializer(request.user).data)
    def put(self, request):
        s = UserUpdateSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True); s.save()
        return Response({'mensagem': 'Perfil atualizado.', 'usuario': UserDetailSerializer(request.user).data})

class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        qs = User.objects.filter(is_active=True).exclude(perfil=PerfilUsuario.CLIENTE)
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(nome__icontains=search)|Q(email__icontains=search)|Q(username__icontains=search))
        p = StandardPagination(); page = p.paginate_queryset(qs, request)
        return p.get_paginated_response(UserListSerializer(page, many=True).data)
    def post(self, request):
        s = UserCreateSerializer(data=request.data); s.is_valid(raise_exception=True)
        u = s.save()
        return Response({'mensagem': 'Usuário criado.', 'usuario': UserDetailSerializer(u).data}, status=201)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def _get(self, pk):
        try: return User.objects.exclude(perfil=PerfilUsuario.CLIENTE).get(pk=pk)
        except User.DoesNotExist: return None
    def get(self, request, pk):
        u = self._get(pk)
        if not u: return Response({'mensagem': 'Não encontrado.'}, status=404)
        return Response(UserDetailSerializer(u).data)
    def put(self, request, pk):
        u = self._get(pk)
        if not u: return Response({'mensagem': 'Não encontrado.'}, status=404)
        s = UserUpdateSerializer(u, data=request.data, partial=True)
        s.is_valid(raise_exception=True); s.save()
        return Response({'mensagem': 'Atualizado.', 'usuario': UserDetailSerializer(u).data})
    def delete(self, request, pk):
        u = self._get(pk)
        if not u: return Response({'mensagem': 'Não encontrado.'}, status=404)
        if u == request.user: return Response({'mensagem': 'Não pode desativar sua própria conta.'}, status=400)
        u.is_active = False; u.save()
        return Response({'mensagem': 'Usuário desativado.'})

class ClienteListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        qs = User.objects.filter(perfil=PerfilUsuario.CLIENTE)
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(nome__icontains=search)|Q(email__icontains=search)|Q(cpf__icontains=search)|Q(username__icontains=search))
        p = StandardPagination(); page = p.paginate_queryset(qs, request)
        return p.get_paginated_response(ClienteListSerializer(page, many=True).data)
    def post(self, request):
        s = ClienteCreateSerializer(data=request.data); s.is_valid(raise_exception=True)
        c = s.save()
        return Response({'mensagem': 'Cliente criado.', 'cliente': ClienteDetailSerializer(c).data}, status=201)

class ClienteDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def _get(self, pk):
        try: return User.objects.get(pk=pk, perfil=PerfilUsuario.CLIENTE)
        except User.DoesNotExist: return None
    def get(self, request, pk):
        c = self._get(pk)
        if not c: return Response({'mensagem': 'Não encontrado.'}, status=404)
        return Response(ClienteDetailSerializer(c).data)
    def put(self, request, pk):
        c = self._get(pk)
        if not c: return Response({'mensagem': 'Não encontrado.'}, status=404)
        s = ClienteUpdateSerializer(c, data=request.data, partial=True)
        s.is_valid(raise_exception=True); s.save()
        return Response({'mensagem': 'Cliente atualizado.', 'cliente': ClienteDetailSerializer(c).data})

class ClientePontosView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request, pk):
        try: c = User.objects.get(pk=pk, perfil=PerfilUsuario.CLIENTE)
        except User.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        from django.conf import settings
        limite = getattr(settings, 'COMPRAS_PARA_VOUCHER', 10)
        return Response({
            'cliente_id': c.id, 'nome': c.nome, 'saldo_pontos': c.saldo_pontos,
            'total_compras': c.total_compras, 'vouchers_disponiveis': c.vouchers_disponiveis,
            'proxima_compra_voucher': limite - (c.total_compras % limite),
            'total_pontos_ganhos': c.total_pontos_ganhos,
            'total_pontos_resgatados': c.total_pontos_resgatados,
        })

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        from rest_framework_simplejwt.views import TokenRefreshView
        return TokenRefreshView.as_view()(request._request)
