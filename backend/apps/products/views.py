import os
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.products.models import Produto, Categoria
from apps.products.serializers import (
    CategoriaSerializer, ProdutoListSerializer,
    ProdutoDetailSerializer, ProdutoCreateSerializer, ProdutoUpdateSerializer,
)
from apps.core.choices import StatusEstoque, UnidadeMedida
from apps.core.pagination import StandardPagination
from flor_dende.jwt_auth.permissions import IsAdminOrFuncionario

logger = logging.getLogger(__name__)


def gerar_imagem_barcode(produto):
    """Gera imagem do código de barras e salva no produto."""
    try:
        import barcode
        from barcode.writer import ImageWriter
        from django.core.files import File
        from django.conf import settings
        import io

        codigo = produto.codigo_barras or produto.codigo
        # Remove caracteres inválidos
        codigo_clean = ''.join(filter(str.isalnum, codigo))
        if not codigo_clean:
            return

        # Usa Code128 (aceita qualquer código alfanumérico)
        barcode_class = barcode.get_barcode_class('code128')
        buf = io.BytesIO()
        bc  = barcode_class(codigo_clean, writer=ImageWriter())
        bc.write(buf, options={'module_height': 10, 'font_size': 6, 'text_distance': 2})
        buf.seek(0)

        nome_arquivo = f'barcode_{produto.codigo}.png'
        produto.imagem_codigo_barras.save(nome_arquivo, File(buf), save=True)
    except Exception as e:
        logger.error(f"Erro ao gerar código de barras: {e}")


class CategoriaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def get(self, request):
        qs = Categoria.objects.filter(ativo=True).order_by('nome')
        search = request.query_params.get('search')
        if search: qs = qs.filter(nome__icontains=search)
        p = StandardPagination()
        page = p.paginate_queryset(qs, request)
        return p.get_paginated_response(CategoriaSerializer(page, many=True).data)

    def post(self, request):
        nome = request.data.get('nome', '').strip()
        if not nome:
            return Response({'mensagem': 'Nome é obrigatório.'}, status=400)
        if Categoria.objects.filter(nome__iexact=nome, ativo=True).exists():
            return Response({'mensagem': 'Categoria já existe.'}, status=400)
        c = Categoria.objects.create(
            nome=nome, descricao=request.data.get('descricao',''), criado_por=request.user
        )
        return Response({'mensagem': 'Categoria criada.', 'categoria': CategoriaSerializer(c).data}, status=201)


class CategoriaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def _get(self, pk):
        try: return Categoria.objects.get(pk=pk, ativo=True)
        except Categoria.DoesNotExist: return None

    def put(self, request, pk):
        c = self._get(pk)
        if not c: return Response({'mensagem': 'Não encontrada.'}, status=404)
        nome = request.data.get('nome', c.nome).strip()
        if not nome: return Response({'mensagem': 'Nome é obrigatório.'}, status=400)
        c.nome = nome; c.descricao = request.data.get('descricao', c.descricao); c.save()
        return Response({'mensagem': 'Categoria atualizada.', 'categoria': CategoriaSerializer(c).data})

    def delete(self, request, pk):
        c = self._get(pk)
        if not c: return Response({'mensagem': 'Não encontrada.'}, status=404)
        c.ativo = False; c.save()
        return Response({'mensagem': 'Categoria removida.'})


class ProdutoListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def get(self, request):
        qs = Produto.objects.filter(ativo=True).select_related('categoria')
        search = request.query_params.get('search')
        cat    = request.query_params.get('categoria')
        stk    = request.query_params.get('status_estoque')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(nome__icontains=search)|Q(codigo__icontains=search)|Q(codigo_barras__icontains=search))
        if cat: qs = qs.filter(categoria_id=cat)
        if stk: qs = qs.filter(status_estoque=stk)
        p = StandardPagination(); page = p.paginate_queryset(qs.order_by('nome'), request)
        return p.get_paginated_response(ProdutoListSerializer(page, many=True, context={'request': request}).data)

    def post(self, request):
        s = ProdutoCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            produto = s.save(criado_por=request.user)
            if 'imagem' in request.FILES:
                produto.imagem = request.FILES['imagem']; produto.save(update_fields=['imagem'])
            # Gera código de barras automaticamente
            gerar_imagem_barcode(produto)
            produto.atualizar_status_estoque()
            return Response({'mensagem': 'Produto criado.',
                             'produto': ProdutoDetailSerializer(produto, context={'request': request}).data}, status=201)
        except Exception as e:
            return Response({'mensagem': str(e)}, status=400)


class ProdutoDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def _get(self, pk):
        try: return Produto.objects.get(pk=pk, ativo=True)
        except Produto.DoesNotExist: return None

    def get(self, request, pk):
        p = self._get(pk)
        if not p: return Response({'mensagem': 'Não encontrado.'}, status=404)
        return Response(ProdutoDetailSerializer(p, context={'request': request}).data)

    def patch(self, request, pk):
        p = self._get(pk)
        if not p: return Response({'mensagem': 'Não encontrado.'}, status=404)
        s = ProdutoUpdateSerializer(p, data=request.data, partial=True)
        s.is_valid(raise_exception=True); s.save(atualizado_por=request.user)
        if 'imagem' in request.FILES:
            p.imagem = request.FILES['imagem']; p.save(update_fields=['imagem'])
        # Regenera código de barras se código foi atualizado
        if 'codigo_barras' in request.data:
            gerar_imagem_barcode(p)
        p.atualizar_status_estoque()
        return Response({'mensagem': 'Produto atualizado.',
                         'produto': ProdutoDetailSerializer(p, context={'request': request}).data})

    def delete(self, request, pk):
        p = self._get(pk)
        if not p: return Response({'mensagem': 'Não encontrado.'}, status=404)
        p.deletar(usuario=request.user)
        return Response({'mensagem': 'Produto desativado.'})


class ProdutoPDVSearchView(APIView):
    """Busca rápida para o PDV — por nome, código ou código de barras."""
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 1: return Response({'resultados': []})
        from django.db.models import Q
        produtos = Produto.objects.filter(
            Q(nome__icontains=q)|Q(codigo__iexact=q)|Q(codigo_barras__iexact=q), ativo=True
        ).select_related('categoria')[:20]
        return Response({'resultados': ProdutoListSerializer(produtos, many=True, context={'request': request}).data})


class AlertasEstoqueView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def get(self, request):
        alertas = Produto.objects.filter(
            status_estoque__in=[StatusEstoque.BAIXO, StatusEstoque.ZERADO], ativo=True
        ).select_related('categoria').order_by('quantidade_estoque')
        return Response({
            'total':   alertas.count(),
            'alertas': ProdutoListSerializer(alertas, many=True, context={'request': request}).data,
        })


class GerarBarcodeView(APIView):
    """POST /api/products/{id}/barcode/ — (Re)gera código de barras do produto."""
    permission_classes = [IsAuthenticated, IsAdminOrFuncionario]

    def post(self, request, pk):
        try: p = Produto.objects.get(pk=pk, ativo=True)
        except Produto.DoesNotExist: return Response({'mensagem': 'Não encontrado.'}, status=404)
        gerar_imagem_barcode(p)
        p.refresh_from_db()
        return Response({
            'mensagem': 'Código de barras gerado.',
            'imagem_barcode_url': request.build_absolute_uri(p.imagem_codigo_barras.url) if p.imagem_codigo_barras else None
        })
