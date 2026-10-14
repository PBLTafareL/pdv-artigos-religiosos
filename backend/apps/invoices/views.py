import os
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse, HttpResponse
from apps.invoices.models import NotaFiscal
from apps.invoices.services import InvoiceService
from apps.pdv.models import VendaPDV
from apps.core.pagination import StandardPagination
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

class NotaListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        qs = NotaFiscal.objects.select_related('cliente','venda').order_by('-emitida_em')
        p  = StandardPagination(); page = p.paginate_queryset(qs, request)
        data = [{'id': n.id, 'numero': n.numero, 'cliente_nome': n.cliente.nome if n.cliente else None,
                 'total': float(n.total), 'status': n.status, 'status_display': n.get_status_display(),
                 'emitida_em': n.emitida_em, 'arquivo_pdf': bool(n.arquivo_pdf)} for n in page]
        return p.get_paginated_response(data)

class EmitirNotaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        try:
            venda = VendaPDV.objects.get(pk=venda_id)
            nota  = InvoiceService.emitir(venda, request.user)
            return Response({'mensagem': f'Nota {nota.numero} emitida.', 'nota_id': nota.id,
                             'numero': nota.numero}, status=201)
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class DownloadNotaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request, pk):
        try: nota = NotaFiscal.objects.get(pk=pk)
        except NotaFiscal.DoesNotExist: return Response({'mensagem': 'Não encontrada.'}, status=404)
        if not nota.arquivo_pdf:
            # Tenta regerar
            try:
                pdf = InvoiceService._gerar_pdf(nota, nota.venda)
                return HttpResponse(pdf, content_type='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename="{nota.numero}.pdf"'})
            except: return Response({'mensagem': 'PDF não disponível.'}, status=404)
        from django.conf import settings
        path = os.path.join(settings.MEDIA_ROOT, str(nota.arquivo_pdf))
        if os.path.exists(path):
            return FileResponse(open(path,'rb'), content_type='application/pdf',
                                as_attachment=True, filename=f'{nota.numero}.pdf')
        return Response({'mensagem': 'Arquivo não encontrado.'}, status=404)

class CancelarNotaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, pk):
        motivo = request.data.get('motivo','')
        if not motivo: return Response({'mensagem': 'Informe o motivo.'}, status=400)
        try:
            nota = InvoiceService.cancelar(pk, motivo, request.user)
            return Response({'mensagem': f'Nota {nota.numero} cancelada.'})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)
