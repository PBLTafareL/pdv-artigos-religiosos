import logging
from io import BytesIO
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from apps.invoices.models import NotaFiscal
from apps.core.utils import formatar_moeda

logger = logging.getLogger(__name__)

class InvoiceService:
    @staticmethod
    def gerar_numero():
        ano    = timezone.now().year
        ultimo = NotaFiscal.objects.filter(numero__startswith=f'NF-{ano}-').count()
        return f'NF-{ano}-{str(ultimo+1).zfill(4)}'

    @staticmethod
    def emitir(venda, usuario):
        from apps.core.choices import StatusVenda
        if venda.status != StatusVenda.CONCLUIDA:
            raise ValueError('Apenas vendas concluídas podem ter nota emitida.')
        if hasattr(venda, 'nota_fiscal'):
            return venda.nota_fiscal
        nota = NotaFiscal.objects.create(
            numero=InvoiceService.gerar_numero(), venda=venda,
            cliente=venda.cliente, total=venda.total, criado_por=usuario
        )
        try:
            pdf = InvoiceService._gerar_pdf(nota, venda)
            from django.core.files.base import ContentFile
            nota.arquivo_pdf.save(f'{nota.numero}.pdf', ContentFile(pdf), save=True)
        except Exception as e:
            logger.error(f"Erro ao gerar PDF da NF {nota.numero}: {e}")
        return nota

    @staticmethod
    def _gerar_pdf(nota, venda):
        buf    = BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        els    = []
        verde  = colors.HexColor('#2d6a4f')

        titulo = ParagraphStyle('t', parent=styles['Title'], fontSize=18, textColor=verde, alignment=TA_CENTER, spaceAfter=4)
        sub    = ParagraphStyle('s', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=2)
        lbl    = ParagraphStyle('l', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        bold   = ParagraphStyle('b', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')

        els += [Paragraph('🌸 Flor de Dendê PDV', titulo),
                Paragraph(f'NOTA FISCAL — {nota.numero}', sub),
                Paragraph(f'Emitida em: {nota.emitida_em.strftime("%d/%m/%Y às %H:%M")}', sub),
                HRFlowable(width='100%', thickness=1, color=verde), Spacer(1, .3*cm)]

        if nota.cliente:
            els += [Paragraph('CLIENTE', lbl), Paragraph(nota.cliente.nome, bold)]
            if nota.cliente.cpf: els.append(Paragraph(f'CPF: {nota.cliente.cpf}', styles['Normal']))
            els.append(Spacer(1, .3*cm))

        els += [Paragraph('OPERADOR', lbl), Paragraph(venda.operador.nome, styles['Normal']),
                Spacer(1, .4*cm), HRFlowable(width='100%', thickness=.5, color=colors.lightgrey), Spacer(1, .3*cm)]

        header = [['Produto','Qtd','Un','Preço','Total']]
        dados  = [[i.produto.nome[:25], str(i.quantidade), i.produto.unidade_medida,
                   formatar_moeda(i.preco_unitario), formatar_moeda(i.total)] for i in venda.itens.all()]
        tab = Table(header+dados, colWidths=[7*cm,2*cm,1.5*cm,3*cm,3*cm])
        tab.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),verde),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),.5,colors.lightgrey),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0f7f4')]),
        ]))
        els += [Paragraph('ITENS', lbl), Spacer(1,.2*cm), tab, Spacer(1,.4*cm)]

        total_style = ParagraphStyle('ts', parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', alignment=TA_RIGHT)
        els.append(Paragraph(f'Subtotal: {formatar_moeda(venda.subtotal)}', styles['Normal']))
        if venda.desconto_valor > 0:
            els.append(Paragraph(f'Desconto: - {formatar_moeda(venda.desconto_valor)}', styles['Normal']))
        els += [Spacer(1,.2*cm), Paragraph(f'TOTAL: {formatar_moeda(venda.total)}', total_style)]

        if venda.pontos_gerados > 0:
            pts_style = ParagraphStyle('ps', parent=styles['Normal'], textColor=verde, fontName='Helvetica-Bold')
            els += [Spacer(1,.3*cm), Paragraph(f'🏆 Pontos gerados: {venda.pontos_gerados}', pts_style)]

        rodape_style = ParagraphStyle('rs', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.grey)
        els += [Spacer(1,.5*cm), HRFlowable(width='100%', thickness=1, color=verde),
                Paragraph('Obrigado pela preferência! — Flor de Dendê PDV', rodape_style)]

        doc.build(els)
        return buf.getvalue()

    @staticmethod
    def cancelar(nota_id, motivo, usuario):
        try: nota = NotaFiscal.objects.get(pk=nota_id)
        except NotaFiscal.DoesNotExist: raise ValueError('Nota não encontrada.')
        if nota.status == 'cancelada': raise ValueError('Nota já cancelada.')
        nota.status = 'cancelada'; nota.cancelada_em = timezone.now()
        nota.motivo_cancelamento = motivo; nota.save()
        return nota
