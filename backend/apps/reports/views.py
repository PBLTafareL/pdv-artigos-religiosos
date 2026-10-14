from datetime import date
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.reports.services import ReportService
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

def parse_dates(request):
    try:
        di = date.fromisoformat(request.query_params.get('data_inicio', str(date.today())))
        df = date.fromisoformat(request.query_params.get('data_fim',    str(date.today())))
        return di, df, None
    except ValueError:
        return None, None, Response({'mensagem': 'Datas inválidas. Use YYYY-MM-DD.'}, status=400)

class RelVendasView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        di, df, err = parse_dates(request)
        if err: return err
        fmt = request.query_params.get('formato','json')
        if fmt == 'pdf':
            pdf  = ReportService.pdf_vendas(di, df)
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="vendas_{di}_{df}.pdf"'
            return resp
        return Response(ReportService.vendas(di, df))

class RelProdutosView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        di, df, err = parse_dates(request)
        if err: return err
        dados = ReportService.produtos_vendidos(di, df)
        return Response([{'produto__codigo': d['produto__codigo'], 'produto__nome': d['produto__nome'],
                           'total_qty': float(d['total_qty'] or 0), 'total_valor': float(d['total_valor'] or 0)} for d in dados])

class RelEstoqueView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        fmt = request.query_params.get('formato','json')
        if fmt == 'pdf':
            pdf  = ReportService.pdf_estoque()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = 'attachment; filename="estoque.pdf"'
            return resp
        return Response(ReportService.estoque())
