import logging
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from apps.pdv.models import SessaoCaixa, VendaPDV, ItemVenda, PagamentoPDV
from apps.products.models import Produto
from apps.core.choices import StatusCaixa, StatusVenda, FormaPagamento
from apps.core.exceptions import CaixaFechadoError, CaixaJaAbertoError, EstoqueInsuficienteError
from apps.core.utils import calcular_pontos

logger = logging.getLogger(__name__)


class CaixaService:
    @staticmethod
    def abrir(operador, fundo=0):
        if SessaoCaixa.objects.filter(operador=operador, status=StatusCaixa.ABERTO).exists():
            raise CaixaJaAbertoError()
        return SessaoCaixa.objects.create(
            operador=operador, fundo_caixa=Decimal(str(fundo)),
            saldo_calculado=Decimal(str(fundo)), criado_por=operador
        )

    @staticmethod
    def fechar(sessao_id, operador):
        try:
            sessao = SessaoCaixa.objects.get(pk=sessao_id, operador=operador, status=StatusCaixa.ABERTO)
        except SessaoCaixa.DoesNotExist:
            raise ValueError('Caixa não encontrado ou já fechado.')
        sessao.status = StatusCaixa.FECHADO
        sessao.fechado_em = timezone.now()
        sessao.save()
        return sessao

    @staticmethod
    def get_aberto(operador):
        try:
            return SessaoCaixa.objects.get(operador=operador, status=StatusCaixa.ABERTO)
        except SessaoCaixa.DoesNotExist:
            raise CaixaFechadoError()


class VendaService:
    @staticmethod
    def iniciar(operador, tipo='venda'):
        sessao = CaixaService.get_aberto(operador)
        return VendaPDV.objects.create(
            sessao=sessao, operador=operador, tipo=tipo,
            status=StatusVenda.ABERTA, criado_por=operador
        )

    @staticmethod
    def adicionar_item(venda_id, produto_id, quantidade, operador):
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        produto = Produto.objects.get(pk=produto_id, ativo=True)
        qtd = Decimal(str(quantidade))

        if produto.quantidade_estoque < qtd:
            raise EstoqueInsuficienteError(produto.nome, float(produto.quantidade_estoque), float(qtd))

        # Soma se já existe no carrinho
        item = ItemVenda.objects.filter(venda=venda, produto=produto).first()
        if item:
            item.quantidade += qtd
            item.total = item.quantidade * item.preco_unitario
            item.save()
        else:
            ItemVenda.objects.create(
                venda=venda, produto=produto, quantidade=qtd,
                preco_unitario=produto.preco_venda,
                total=qtd * produto.preco_venda
            )
        VendaService._recalcular(venda)
        return venda

    @staticmethod
    def remover_item(venda_id, item_id, operador):
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        ItemVenda.objects.filter(pk=item_id, venda=venda).delete()
        VendaService._recalcular(venda)
        return venda

    @staticmethod
    def _recalcular(venda):
        subtotal = sum(i.total for i in venda.itens.all())
        venda.subtotal = subtotal
        venda.total    = max(Decimal('0'), subtotal - venda.desconto_valor)
        venda.save(update_fields=['subtotal','total','atualizado_em'])

    @staticmethod
    def vincular_cliente(venda_id, cliente_id, operador):
        from apps.accounts.models import User
        from apps.core.choices import PerfilUsuario
        venda   = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        cliente = User.objects.get(pk=cliente_id, perfil=PerfilUsuario.CLIENTE)
        venda.cliente = cliente
        venda.save(update_fields=['cliente','atualizado_em'])
        return venda, cliente

    @staticmethod
    def aplicar_voucher(venda_id, operador):
        from django.conf import settings
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        if not venda.cliente: raise ValueError('Vincule um cliente antes de usar o voucher.')
        if venda.cliente.vouchers_disponiveis <= 0: raise ValueError('Cliente não possui vouchers.')
        valor_voucher = Decimal(str(getattr(settings, 'VALOR_VOUCHER', 50)))
        venda.cliente.usar_voucher()
        venda.desconto_valor = (venda.desconto_valor or 0) + valor_voucher
        venda.total = max(Decimal('0'), venda.subtotal - venda.desconto_valor)
        venda.save(update_fields=['desconto_valor','total','atualizado_em'])
        return venda

    @staticmethod
    def registrar_pagamento(venda_id, dados, operador):
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        PagamentoPDV.objects.filter(venda=venda).delete()
        valor = Decimal(str(dados['valor']))
        troco = max(Decimal('0'), valor - venda.total) if dados['forma_pagamento'] == 'dinheiro' else Decimal('0')
        PagamentoPDV.objects.create(
            venda=venda, forma_pagamento=dados['forma_pagamento'],
            valor=valor, troco=troco
        )
        return venda

    @staticmethod
    def finalizar(venda_id, operador, usar_voucher=False):
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)

        if usar_voucher and venda.cliente and venda.cliente.vouchers_disponiveis > 0:
            venda = VendaService.aplicar_voucher(venda_id, operador)
            venda.refresh_from_db()

        # Baixa estoque
        for item in venda.itens.all():
            item.produto.quantidade_estoque -= item.quantidade
            item.produto.save(update_fields=['quantidade_estoque'])
            item.produto.atualizar_status_estoque()

        # Pontos e voucher
        pontos = calcular_pontos(venda.total)
        ganhou_voucher = False
        if venda.cliente and pontos > 0:
            venda.cliente.creditar_pontos(pontos)
            ganhou_voucher = venda.cliente.registrar_compra()

        venda.pontos_gerados = pontos
        venda.status         = StatusVenda.CONCLUIDA
        venda.finalizada_em  = timezone.now()
        venda.atualizado_por = operador
        venda.save(update_fields=['pontos_gerados','status','finalizada_em','atualizado_por','atualizado_em'])

        # Atualiza caixa
        s = venda.sessao
        s.total_vendas    = (s.total_vendas or 0) + venda.total
        s.saldo_calculado = (s.fundo_caixa or 0) + s.total_vendas
        s.save(update_fields=['total_vendas','saldo_calculado'])

        logger.info(f"Venda #{venda.pk} finalizada | Total: R${venda.total} | Pontos: {pontos}")
        return venda, pontos, ganhou_voucher

    @staticmethod
    def cancelar(venda_id, operador):
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        venda.status = StatusVenda.CANCELADA
        venda.atualizado_por = operador
        venda.save(update_fields=['status','atualizado_por','atualizado_em'])
        return venda

    @staticmethod
    def salvar_como_orcamento(venda_id, validade, observacao, operador):
        from apps.quotations.models import Orcamento, ItemOrcamento
        from apps.core.choices import StatusOrcamento
        venda = VendaPDV.objects.get(pk=venda_id, status=StatusVenda.ABERTA)
        if not venda.cliente: raise ValueError('Vincule um cliente antes de salvar como orçamento.')
        ano    = timezone.now().year
        ultimo = Orcamento.objects.filter(numero__startswith=f'ORC-{ano}-').count()
        numero = f'ORC-{ano}-{str(ultimo+1).zfill(4)}'
        orc = Orcamento.objects.create(
            numero=numero, cliente=venda.cliente, responsavel=venda.operador,
            status=StatusOrcamento.ABERTO, validade=validade,
            subtotal=venda.subtotal, desconto_valor=venda.desconto_valor,
            total=venda.total, observacao=observacao, venda_pdv=venda, criado_por=operador
        )
        for item in venda.itens.all():
            ItemOrcamento.objects.create(
                orcamento=orc, produto=item.produto, quantidade=item.quantidade,
                preco_unitario=item.preco_unitario, total=item.total
            )
        venda.status = StatusVenda.CANCELADA
        venda.save(update_fields=['status','atualizado_em'])
        return orc
