import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.pdv.models import SessaoCaixa, VendaPDV
from apps.pdv.serializers import (
    AbrirCaixaSerializer, IniciarVendaSerializer, AdicionarItemSerializer,
    PagamentoSerializer, SessaoCaixaSerializer,
    VendaPDVDetailSerializer, VendaPDVListSerializer,
)
from apps.pdv.services import CaixaService, VendaService
from apps.core.choices import StatusCaixa, StatusVenda
from apps.core.pagination import StandardPagination
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

logger = logging.getLogger(__name__)


class AbrirCaixaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request):
        s = AbrirCaixaSerializer(data=request.data); s.is_valid(raise_exception=True)
        try:
            sessao = CaixaService.abrir(request.user, s.validated_data.get('fundo_caixa', 0))
            return Response({'mensagem': 'Caixa aberto.', 'sessao': SessaoCaixaSerializer(sessao).data}, status=201)
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class CaixaAtualView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        try:
            s = SessaoCaixa.objects.get(operador=request.user, status=StatusCaixa.ABERTO)
            return Response(SessaoCaixaSerializer(s).data)
        except SessaoCaixa.DoesNotExist:
            return Response({'mensagem': 'Nenhum caixa aberto.'}, status=404)

class FecharCaixaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, sessao_id):
        try:
            s = CaixaService.fechar(sessao_id, request.user)
            return Response({'mensagem': 'Caixa fechado.', 'sessao': SessaoCaixaSerializer(s).data})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class IniciarVendaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request):
        s = IniciarVendaSerializer(data=request.data); s.is_valid(raise_exception=True)
        try:
            venda = VendaService.iniciar(request.user, s.validated_data.get('tipo','venda'))
            return Response({'mensagem': 'Venda iniciada.', 'venda': VendaPDVDetailSerializer(venda).data}, status=201)
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class VendaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request, venda_id):
        try:
            v = VendaPDV.objects.get(pk=venda_id)
            return Response(VendaPDVDetailSerializer(v).data)
        except VendaPDV.DoesNotExist: return Response({'mensagem': 'Não encontrada.'}, status=404)

class AdicionarItemView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        s = AdicionarItemSerializer(data=request.data); s.is_valid(raise_exception=True)
        try:
            v = VendaService.adicionar_item(
                venda_id, s.validated_data['produto_id'],
                s.validated_data['quantidade'], request.user)
            return Response({'mensagem': 'Item adicionado.', 'venda': VendaPDVDetailSerializer(v).data})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class RemoverItemView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def delete(self, request, venda_id, item_id):
        try:
            v = VendaService.remover_item(venda_id, item_id, request.user)
            return Response({'mensagem': 'Item removido.', 'venda': VendaPDVDetailSerializer(v).data})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class VincularClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        from django.conf import settings
        cliente_id = request.data.get('cliente_id')
        if not cliente_id: return Response({'mensagem': 'cliente_id é obrigatório.'}, status=400)
        try:
            venda, cliente = VendaService.vincular_cliente(venda_id, cliente_id, request.user)
            limite = getattr(settings, 'COMPRAS_PARA_VOUCHER', 10)
            return Response({
                'mensagem': f'Cliente {cliente.nome} vinculado.',
                'venda': VendaPDVDetailSerializer(venda).data,
                'cliente': {
                    'id': cliente.id, 'nome': cliente.nome,
                    'saldo_pontos': cliente.saldo_pontos,
                    'vouchers_disponiveis': cliente.vouchers_disponiveis,
                    'total_compras': cliente.total_compras,
                    'proxima_compra_voucher': limite - (cliente.total_compras % limite),
                }
            })
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class AplicarVoucherView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        try:
            v = VendaService.aplicar_voucher(venda_id, request.user)
            return Response({'mensagem': 'Voucher de R$50 aplicado!', 'venda': VendaPDVDetailSerializer(v).data})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class RegistrarPagamentoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        s = PagamentoSerializer(data=request.data); s.is_valid(raise_exception=True)
        try:
            v = VendaService.registrar_pagamento(venda_id, s.validated_data, request.user)
            return Response({'mensagem': 'Pagamento registrado.', 'venda': VendaPDVDetailSerializer(v).data})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class FinalizarVendaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        usar_voucher = request.data.get('usar_voucher', False)
        try:
            venda, pontos, ganhou = VendaService.finalizar(venda_id, request.user, usar_voucher)
            resp = {'mensagem': 'Venda finalizada!', 'pontos_gerados': pontos,
                    'ganhou_voucher': ganhou, 'venda': VendaPDVDetailSerializer(venda).data}
            if ganhou:
                from django.conf import settings
                valor = getattr(settings, 'VALOR_VOUCHER', 50)
                resp['mensagem_voucher'] = f'🎉 Cliente ganhou voucher de R${valor},00 por completar 10 compras!'
            return Response(resp)
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class CancelarVendaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        try:
            VendaService.cancelar(venda_id, request.user)
            return Response({'mensagem': 'Venda cancelada.'})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class SalvarOrcamentoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, venda_id):
        validade   = request.data.get('validade')
        observacao = request.data.get('observacao', '')
        if not validade: return Response({'mensagem': 'Informe a validade do orçamento.'}, status=400)
        try:
            orc = VendaService.salvar_como_orcamento(venda_id, validade, observacao, request.user)
            return Response({'mensagem': f'Orçamento {orc.numero} salvo com sucesso!', 'numero': orc.numero})
        except Exception as e: return Response({'mensagem': str(e)}, status=400)

class VendaListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        qs = VendaPDV.objects.filter(tipo='venda', status=StatusVenda.CONCLUIDA).order_by('-criado_em')
        p  = StandardPagination(); page = p.paginate_queryset(qs, request)
        return p.get_paginated_response(VendaPDVListSerializer(page, many=True).data)
