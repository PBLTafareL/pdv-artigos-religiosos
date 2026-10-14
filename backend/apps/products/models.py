from django.db import models
from django.conf import settings
from apps.core.models import ModeloBase
from apps.core.choices import UnidadeMedida, StatusEstoque

class Categoria(ModeloBase):
    nome      = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'products_categoria'
        ordering = ['nome']
    def __str__(self): return self.nome

class Produto(ModeloBase):
    codigo          = models.CharField(max_length=50, unique=True)
    codigo_barras   = models.CharField(max_length=50, null=True, blank=True, unique=True)
    nome            = models.CharField(max_length=200)
    descricao       = models.TextField(blank=True, null=True)
    categoria       = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')
    preco_custo     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda     = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    estoque_minimo  = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unidade_medida  = models.CharField(max_length=5, choices=UnidadeMedida.CHOICES, default='un')
    status_estoque  = models.CharField(max_length=10, choices=StatusEstoque.CHOICES, default=StatusEstoque.NORMAL)
    imagem          = models.ImageField(upload_to='produtos/', null=True, blank=True)
    imagem_codigo_barras = models.ImageField(upload_to='codigos_barras/', null=True, blank=True)

    class Meta:
        db_table = 'products_produto'
        ordering = ['nome']

    def __str__(self): return f'{self.codigo} — {self.nome}'

    def get_status_estoque_display(self):
        return dict(StatusEstoque.CHOICES).get(self.status_estoque, self.status_estoque)

    def atualizar_status_estoque(self):
        if self.quantidade_estoque <= 0:
            self.status_estoque = StatusEstoque.ZERADO
        elif self.quantidade_estoque <= self.estoque_minimo:
            self.status_estoque = StatusEstoque.BAIXO
        else:
            self.status_estoque = StatusEstoque.NORMAL
        self.save(update_fields=['status_estoque'])

    @property
    def e_inteiro(self):
        return self.unidade_medida in UnidadeMedida.INTEIRAS
