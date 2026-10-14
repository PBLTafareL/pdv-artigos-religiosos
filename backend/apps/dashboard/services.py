from django.utils.timezone import localdate, make_aware
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta, datetime, time

def _range_hoje():
    """Retorna início e fim do dia de hoje no fuso local, como datetimes aware."""
    hoje   = localdate()
    inicio = make_aware(datetime.combine(hoje, time.min))
    fim    = make_aware(datetime.combine(hoje, time.max))
    return inicio, fim

def _range_dias(dias):
    """Retorna início do período e fim de hoje como datetimes aware."""
    hoje   = localdate()
    inicio = make_aware(datetime.combine(hoje - timedelta(days=dias), time.min))
    fim    = make_aware(datetime.combine(hoje, time.max))
    return inicio, fim

class DashboardService:
    @staticmethod
    def resumo():
        from apps.pdv.models import VendaPDV
        from apps.quotations.models import Orcamento
        from apps.core.choices import StatusVenda, StatusOrcamento

        inicio, fim = _range_hoje()

        # Busca por finalizada_em OU criado_em (para vendas sem finalizada_em preenchido)
        vendas = VendaPDV.objects.filter(
            Q(finalizada_em__gte=inicio, finalizada_em__lte=fim) |
            Q(finalizada_em__isnull=True, criado_em__gte=inicio, criado_em__lte=fim),
            tipo='venda',
            status=StatusVenda.CONCLUIDA
        )

        soma  = vendas.aggregate(v=Sum('total'))['v'] or 0
        media = vendas.aggregate(v=Avg('total'))['v'] or 0
        orcamentos = Orcamento.objects.filter(
            status__in=[StatusOrcamento.ABERTO, StatusOrcamento.APROVADO]
        ).count()

        return {
            'total_vendas_dia':   float(soma),
            'quantidade_vendas':  vendas.count(),
            'ticket_medio':       float(media),
            'orcamentos_abertos': orcamentos,
        }

    @staticmethod
    def alertas():
        from apps.products.models import Produto
        from apps.core.choices import StatusEstoque
        ps = Produto.objects.filter(
            status_estoque__in=[StatusEstoque.BAIXO, StatusEstoque.ZERADO], ativo=True
        ).order_by('quantidade_estoque')
        return {
            'total': ps.count(),
            'alertas': [{
                'id': p.id, 'produto_nome': p.nome, 'produto_codigo': p.codigo,
                'quantidade_atual': float(p.quantidade_estoque),
                'estoque_minimo':   float(p.estoque_minimo),
                'status':           p.status_estoque,
                'status_display':   p.get_status_estoque_display(),
            } for p in ps]
        }

    @staticmethod
    def vendas_por_dia(dias=7):
        from apps.pdv.models import VendaPDV
        from apps.core.choices import StatusVenda
        from django.db.models.functions import TruncDate

        inicio, fim = _range_dias(dias)

        rows = (VendaPDV.objects
            .filter(
                Q(finalizada_em__gte=inicio, finalizada_em__lte=fim) |
                Q(finalizada_em__isnull=True, criado_em__gte=inicio, criado_em__lte=fim),
                tipo='venda',
                status=StatusVenda.CONCLUIDA
            )
            .annotate(dia=TruncDate('criado_em'))
            .values('dia')
            .annotate(soma=Sum('total'), quantidade=Count('id'))
            .order_by('dia')
            .values('dia', 'soma', 'quantidade'))
        return list(rows)

    @staticmethod
    def mais_vendidos(limit=8):
        from apps.pdv.models import ItemVenda
        from apps.core.choices import StatusVenda
        return list(ItemVenda.objects
            .filter(venda__status=StatusVenda.CONCLUIDA, venda__tipo='venda')
            .values('produto__id', 'produto__nome', 'produto__codigo')
            .annotate(total_vendido=Sum('quantidade'), total_receita=Sum('total'))
            .order_by('-total_receita')[:limit])