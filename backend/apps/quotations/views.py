from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
from apps.quotations.models import Orcamento, ItemOrcamento
from apps.core.choices import StatusOrcamento
from apps.core.pagination import StandardPagination
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario


class OrcamentoListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request):
        qs = Orcamento.objects.select_related('cliente','responsavel').filter(ativo=True)
        s  = request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        p = StandardPagination(); page = p.paginate_queryset(qs, request)
        data = [{
            'id': o.id, 'numero': o.numero, 'status': o.status,
            'status_display': o.get_status_display(),
            'cliente_nome': o.cliente.nome, 'responsavel_nome': o.responsavel.nome,
            'subtotal': float(o.subtotal), 'desconto_valor': float(o.desconto_valor),
            'total': float(o.total), 'validade': str(o.validade),
            'esta_expirado': o.esta_expirado,
            'total_itens': o.itens.count(),
            'aprovado_em': o.aprovado_em, 'convertido_em': o.convertido_em,
            'observacao': o.observacao,
            'criado_em': o.criado_em,
        } for o in page]
        return p.get_paginated_response(data)


class OrcamentoDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def get(self, request, pk):
        try: o = Orcamento.objects.get(pk=pk)
        except Orcamento.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        itens = [{'id': i.id, 'produto_nome': i.produto.nome, 'produto_codigo': i.produto.codigo,
                  'unidade_medida': i.produto.unidade_medida,
                  'quantidade': float(i.quantidade), 'preco_unitario': float(i.preco_unitario), 'total': float(i.total)}
                 for i in o.itens.all()]
        return Response({
            'id': o.id, 'numero': o.numero, 'status': o.status, 'status_display': o.get_status_display(),
            'cliente_id': o.cliente_id, 'cliente_nome': o.cliente.nome,
            'cliente_telefone': o.cliente.telefone or '',
            'cliente_email': o.cliente.email or '',
            'responsavel_nome': o.responsavel.nome,
            'subtotal': float(o.subtotal), 'desconto_valor': float(o.desconto_valor), 'total': float(o.total),
            'validade': str(o.validade), 'observacao': o.observacao,
            'aprovado_em': o.aprovado_em, 'recusado_em': o.recusado_em,
            'motivo_recusa': o.motivo_recusa, 'convertido_em': o.convertido_em,
            'itens': itens, 'criado_em': o.criado_em,
        })


class OrcamentoPDFView(APIView):
    """GET /api/quotations/{pk}/pdf/ — Gera PDF do orçamento."""
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def get(self, request, pk):
        try: o = Orcamento.objects.select_related('cliente','responsavel').get(pk=pk)
        except Orcamento.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        try:
            pdf = _gerar_pdf_orcamento(o)
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'inline; filename="orcamento_{o.numero}.pdf"'
            return resp
        except Exception as e:
            return Response({'mensagem': f'Erro ao gerar PDF: {e}'}, status=500)


class AprovarOrcamentoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, pk):
        try: o = Orcamento.objects.get(pk=pk)
        except Orcamento.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        if o.status != StatusOrcamento.ABERTO: return Response({'mensagem': 'Somente orçamentos abertos podem ser aprovados.'}, status=400)
        if o.esta_expirado: return Response({'mensagem': 'Orçamento expirado.'}, status=400)
        o.status = StatusOrcamento.APROVADO; o.aprovado_em = timezone.now(); o.save()
        return Response({'mensagem': f'Orçamento {o.numero} aprovado.'})


class RecusarOrcamentoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, pk):
        motivo = request.data.get('motivo','')
        if not motivo: return Response({'mensagem': 'Informe o motivo da recusa.'}, status=400)
        try: o = Orcamento.objects.get(pk=pk)
        except Orcamento.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        if o.status not in [StatusOrcamento.ABERTO, StatusOrcamento.APROVADO]:
            return Response({'mensagem': 'Orçamento não pode ser recusado.'}, status=400)
        o.status = StatusOrcamento.RECUSADO; o.recusado_em = timezone.now(); o.motivo_recusa = motivo; o.save()
        return Response({'mensagem': f'Orçamento {o.numero} recusado.'})


class ConverterOrcamentoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]
    def post(self, request, pk):
        try: o = Orcamento.objects.get(pk=pk)
        except Orcamento.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        if o.status not in [StatusOrcamento.ABERTO, StatusOrcamento.APROVADO]:
            return Response({'mensagem': f'Orçamento não pode ser convertido.'}, status=400)
        if o.esta_expirado: return Response({'mensagem': 'Orçamento expirado.'}, status=400)
        for item in o.itens.all():
            if item.produto.quantidade_estoque < item.quantidade:
                return Response({'mensagem': f'Estoque insuficiente: {item.produto.nome}'}, status=400)
        from apps.pdv.services import CaixaService
        from apps.pdv.models import VendaPDV, ItemVenda
        try: sessao = CaixaService.get_aberto(request.user)
        except Exception as e: return Response({'mensagem': str(e)}, status=400)
        venda = VendaPDV.objects.create(
            sessao=sessao, operador=request.user, cliente=o.cliente, tipo='venda',
            status='aberta', subtotal=o.subtotal, desconto_valor=o.desconto_valor,
            total=o.total, criado_por=request.user
        )
        for item in o.itens.all():
            ItemVenda.objects.create(venda=venda, produto=item.produto, quantidade=item.quantidade,
                preco_unitario=item.preco_unitario, total=item.total)
        o.status = StatusOrcamento.CONVERTIDO; o.convertido_em = timezone.now(); o.save()
        return Response({'mensagem': f'Orçamento {o.numero} convertido em venda #{venda.pk}.', 'venda_id': venda.pk})


def _gerar_pdf_orcamento(o):
    """Gera o PDF de um orçamento usando ReportLab."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from apps.core.utils import formatar_moeda

    buf    = BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    verde  = colors.HexColor('#2d6a4f')
    amarelo = colors.HexColor('#f59e0b')
    els    = []

    titulo_s = ParagraphStyle('t', parent=styles['Title'], fontSize=20, textColor=verde, spaceAfter=4)
    sub_s    = ParagraphStyle('s', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=2)
    lbl_s    = ParagraphStyle('l', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    bold_s   = ParagraphStyle('b', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')
    dir_s    = ParagraphStyle('r', parent=styles['Normal'], fontSize=11, alignment=TA_RIGHT)

    # Cabeçalho
    els += [
        Paragraph('🌸 Flor de Dendê', titulo_s),
        Paragraph('Produtos Naturais e Espirituais', sub_s),
        HRFlowable(width='100%', thickness=2, color=verde),
        Spacer(1, .3*cm),
        Paragraph(f'ORÇAMENTO Nº {o.numero}', ParagraphStyle('n', parent=styles['Title'], fontSize=14, textColor=amarelo, spaceAfter=2)),
        Paragraph(f'Emitido em: {o.criado_em.strftime("%d/%m/%Y às %H:%M")}  |  Válido até: {o.validade.strftime("%d/%m/%Y")}', sub_s),
        Spacer(1, .4*cm),
    ]

    # Dados do cliente e responsável
    dados_tab = Table([
        [Paragraph('<b>CLIENTE</b>', styles['Normal']), Paragraph('<b>RESPONSÁVEL</b>', styles['Normal'])],
        [Paragraph(o.cliente.nome, bold_s), Paragraph(o.responsavel.nome, bold_s)],
        [Paragraph(o.cliente.email or '', styles['Normal']), Paragraph('Flor de Dendê PDV', styles['Normal'])],
        [Paragraph(o.cliente.telefone or '', styles['Normal']), Paragraph('', styles['Normal'])],
    ], colWidths=[9*cm, 8*cm])
    dados_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f7f4')),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('BOX',        (0,0), (-1,-1), .5, colors.lightgrey),
        ('INNERGRID',  (0,0), (-1,-1), .3, colors.lightgrey),
        ('PADDING',    (0,0), (-1,-1), 6),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
    ]))
    els += [dados_tab, Spacer(1, .4*cm)]

    # Itens
    els.append(Paragraph('ITENS DO ORÇAMENTO', lbl_s))
    els.append(Spacer(1, .2*cm))
    header = [['#', 'Produto', 'Cód.', 'Un.', 'Qtd', 'Preço Unit.', 'Total']]
    rows   = []
    for i, item in enumerate(o.itens.all(), 1):
        from apps.core.choices import UnidadeMedida
        qtd_fmt = str(int(item.quantidade)) if item.produto.unidade_medida in UnidadeMedida.INTEIRAS \
                  else f'{float(item.quantidade):.3f}'
        rows.append([
            str(i), item.produto.nome[:30], item.produto.codigo,
            item.produto.unidade_medida, qtd_fmt,
            formatar_moeda(item.preco_unitario), formatar_moeda(item.total)
        ])

    tab = Table(header + rows, colWidths=[.8*cm, 6.5*cm, 2*cm, 1*cm, 1.5*cm, 2.5*cm, 2.5*cm])
    tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), verde), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (1,1), (1,-1), 'LEFT'),
        ('ALIGN',      (5,0), (-1,-1), 'RIGHT'),
        ('GRID',       (0,0), (-1,-1), .5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')]),
        ('PADDING',    (0,0), (-1,-1), 5),
    ]))
    els += [tab, Spacer(1, .4*cm)]

    # Totais
    totais = []
    if float(o.subtotal) != float(o.total):
        totais.append(['Subtotal:', formatar_moeda(o.subtotal)])
        totais.append([f'Desconto:', f'- {formatar_moeda(o.desconto_valor)}'])
    totais.append(['TOTAL:', formatar_moeda(o.total)])
    tot_tab = Table(totais, colWidths=[13.5*cm, 3.5*cm], hAlign='RIGHT')
    tot_tab.setStyle(TableStyle([
        ('ALIGN',    (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 13),
        ('FONTSIZE', (0,0),  (-1,-2), 9),
        ('TEXTCOLOR',(0,-1), (0,-1), verde),
        ('TEXTCOLOR',(1,-1), (1,-1), verde),
        ('TOPPADDING',  (0,-1), (-1,-1), 4),
        ('LINEABOVE', (0,-1), (-1,-1), 1, verde),
    ]))
    els += [tot_tab, Spacer(1, .4*cm)]

    # Observações
    if o.observacao:
        els += [
            HRFlowable(width='100%', thickness=.5, color=colors.lightgrey),
            Spacer(1, .2*cm),
            Paragraph('OBSERVAÇÕES', lbl_s),
            Paragraph(o.observacao, styles['Normal']),
            Spacer(1, .3*cm),
        ]

    # Validade e assinaturas
    els += [
        HRFlowable(width='100%', thickness=1, color=verde),
        Spacer(1, .3*cm),
        Paragraph(f'Este orçamento é válido até <b>{o.validade.strftime("%d/%m/%Y")}</b>. '
                  f'Após esta data, os preços e condições poderão ser revistos.',
                  ParagraphStyle('v', parent=styles['Normal'], fontSize=9, textColor=colors.grey)),
        Spacer(1, 1*cm),
    ]

    # Linha de assinatura
    assina = Table([
        ['_'*35, '', '_'*35],
        ['Flor de Dendê', '', o.cliente.nome],
        ['Responsável', '', 'Cliente'],
    ], colWidths=[7*cm, 3*cm, 7*cm])
    assina.setStyle(TableStyle([
        ('ALIGN',   (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE',(0,0), (-1,-1), 9),
        ('FONTNAME',(0,1), (-1,1), 'Helvetica-Bold'),
    ]))
    els.append(assina)

    # Rodapé
    els += [
        Spacer(1, .5*cm),
        HRFlowable(width='100%', thickness=.5, color=colors.lightgrey),
        Paragraph('Flor de Dendê — Produtos Naturais e Espirituais',
            ParagraphStyle('f', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)),
    ]

    doc.build(els)
    return buf.getvalue()