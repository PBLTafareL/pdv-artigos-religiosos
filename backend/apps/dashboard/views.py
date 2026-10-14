from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.dashboard.services import DashboardService
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        dias = int(request.query_params.get('dias', 7))
        resumo = DashboardService.resumo()
        return Response({
            'resumo_dia':             resumo,
            'alertas_estoque':        DashboardService.alertas(),
            'vendas_por_dia':         DashboardService.vendas_por_dia(dias),
            'produtos_mais_vendidos': DashboardService.mais_vendidos(),
            'orcamentos_pendentes':   resumo['orcamentos_abertos'],
        })
