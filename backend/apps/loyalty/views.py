from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.loyalty.models import ExtratoPontos
from apps.accounts.models import User
from apps.core.choices import PerfilUsuario
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

class ExtratoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request, cliente_id):
        try: c = User.objects.get(pk=cliente_id, perfil=PerfilUsuario.CLIENTE)
        except User.DoesNotExist: return Response({'mensagem': 'Cliente não encontrado.'}, status=404)
        from django.conf import settings
        limite = getattr(settings, 'COMPRAS_PARA_VOUCHER', 10)
        extrato = ExtratoPontos.objects.filter(cliente=c).order_by('-criado_em')[:50]
        return Response({
            'cliente': c.nome, 'saldo_pontos': c.saldo_pontos,
            'total_pontos_ganhos': c.total_pontos_ganhos,
            'total_pontos_resgatados': c.total_pontos_resgatados,
            'total_compras': c.total_compras,
            'vouchers_disponiveis': c.vouchers_disponiveis,
            'proxima_compra_voucher': limite - (c.total_compras % limite),
            'extrato': [{'id': e.id, 'tipo': e.tipo, 'tipo_display': e.get_tipo_display(),
                         'pontos': e.pontos, 'saldo_apos': e.saldo_apos,
                         'descricao': e.descricao, 'criado_em': e.criado_em} for e in extrato]
        })

class RankingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        clientes = User.objects.filter(perfil=PerfilUsuario.CLIENTE, is_active=True).order_by('-saldo_pontos')[:10]
        from django.conf import settings
        limite = getattr(settings, 'COMPRAS_PARA_VOUCHER', 10)
        return Response([{
            'id': c.id, 'nome': c.nome, 'email': c.email,
            'saldo_pontos': c.saldo_pontos, 'total_pontos_ganhos': c.total_pontos_ganhos,
            'total_compras': c.total_compras, 'vouchers_disponiveis': c.vouchers_disponiveis,
            'proxima_compra_voucher': limite - (c.total_compras % limite),
        } for c in clientes])
