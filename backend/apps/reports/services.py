from io import BytesIO
from django.db.models import Sum, Q
from django.utils.timezone import make_aware
from datetime import datetime, time
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from apps.core.utils import formatar_moeda

def _range(di, df):
    inicio = make_aware(datetime.combine(di, time.min))
    fim    = make_aware(datetime.combine(df, time.max))
    return inicio, fim

class ReportService:
    @staticmethod
    def vendas(di, df):
        from apps.pdv.models import VendaPDV
        from apps.core.choices import StatusVenda
        inicio, fim = _range(di, df)
        qs = VendaPDV.objects.filter(
            Q(finalizada_em__gte=inicio, finalizada_em__lte=fim) |
            Q(finalizada_em__isnull=True, criado_em__gte=inicio, criado_em__lte=fim),
            tipo='venda', status=StatusVenda.CONCLUIDA
        ).select_related('operador','cliente').order_by('-criado_em')
        return [{
            'id':            v.id,
            'criado_em':     (v.finalizada_em or v.criado_em).isoformat(),
            'operador_nome': v.operador.nome,
            'cliente_nome':  v.cliente.nome if v.cliente else None,
            'total_itens':   v.itens.count(),
            'subtotal':      float(v.subtotal),
            'desconto_valor':float(v.desconto_valor),
            'total':         float(v.total),
            'pontos_gerados':v.pontos_gerados,
        } for v in qs]

    @staticmethod
    def produtos_vendidos(di, df):
        from apps.pdv.models import ItemVenda
        from apps.core.choices import StatusVenda
        inicio, fim = _range(di, df)
        rows = ItemVenda.objects.filter(
            Q(venda__finalizada_em__gte=inicio, venda__finalizada_em__lte=fim) |
            Q(venda__finalizada_em__isnull=True, venda__criado_em__gte=inicio, venda__criado_em__lte=fim),
            venda__status=StatusVenda.CONCLUIDA,
            venda__tipo='venda'
        ).values('produto__codigo','produto__nome').annotate(
            qty=Sum('quantidade'), receita=Sum('total')
        ).order_by('-receita')
        return [{
            'produto__codigo': r['produto__codigo'],
            'produto__nome':   r['produto__nome'],
            'total_qty':       float(r['qty'] or 0),
            'total_valor':     float(r['receita'] or 0),
        } for r in rows]

    @staticmethod
    def estoque():
        from apps.products.models import Produto
        return [{
            'id':                 p.id, 'codigo': p.codigo, 'nome': p.nome,
            'categoria_nome':     p.categoria.nome if p.categoria else None,
            'quantidade_estoque': float(p.quantidade_estoque),
            'estoque_minimo':     float(p.estoque_minimo),
            'unidade_medida':     p.unidade_medida,
            'status_estoque':     p.status_estoque,
            'status_display':     p.get_status_estoque_display(),
            'preco_venda':        float(p.preco_venda),
        } for p in Produto.objects.filter(ativo=True).select_related('categoria').order_by('nome')]

    @staticmethod
    def pdf_vendas(di, df):
        dados = ReportService.vendas(di, df)
        buf   = BytesIO()
        doc   = SimpleDocTemplate(buf, pagesize=landscape(A4),
                    rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet(); els = []
        els.append(Paragraph('Flor de Dendê PDV — Relatório de Vendas', styles['Title']))
        els.append(Paragraph(f'Período: {di.strftime("%d/%m/%Y")} a {df.strftime("%d/%m/%Y")}', styles['Normal']))
        els.append(Spacer(1, .5*cm))
        header = [['#','Data','Operador','Cliente','Itens','Total','Pontos']]
        rows   = [[d['id'], d['criado_em'][:16].replace('T',' '),
                   d['operador_nome'] or '-', d['cliente_nome'] or '-',
                   d['total_itens'], formatar_moeda(d['total']), d['pontos_gerados']] for d in dados]
        total  = sum(d['total'] for d in dados)
        if rows: rows.append(['','','','TOTAL GERAL','', formatar_moeda(total),''])
        tab = Table(header+rows, repeatRows=1)
        tab.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2d6a4f')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),.5,colors.lightgrey),
            ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white,colors.HexColor('#f0f7f4')]),
            ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#e8f5e9')),
            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
        ]))
        els.append(tab); doc.build(els); return buf.getvalue()

    @staticmethod
    def pdf_estoque():
        dados  = ReportService.estoque()
        buf    = BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=A4,
                    rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet(); els = []
        from django.utils.timezone import now
        els.append(Paragraph('Flor de Dendê PDV — Relatório de Estoque', styles['Title']))
        els.append(Paragraph(f'Gerado em: {now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
        els.append(Spacer(1, .5*cm))
        header = [['Código','Nome','Categoria','Estoque','Mín','Unid','Status','Preço']]
        rows   = [[d['codigo'], d['nome'][:25], d['categoria_nome'] or '-',
                   str(d['quantidade_estoque']), str(d['estoque_minimo']),
                   d['unidade_medida'], d['status_display'], formatar_moeda(d['preco_venda'])] for d in dados]
        tab = Table(header+rows, repeatRows=1)
        tab.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2d6a4f')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),.5,colors.lightgrey),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0f7f4')]),
        ]))
        els.append(tab); doc.build(els); return buf.getvalue()