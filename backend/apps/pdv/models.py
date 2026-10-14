from django.db import models
from django.conf import settings
from apps.core.choices import StatusCaixa, StatusVenda, FormaPagamento

class SessaoCaixa(models.Model):
    operador       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sessoes_caixa')
    status         = models.CharField(max_length=10, choices=StatusCaixa.CHOICES, default=StatusCaixa.ABERTO)
    fundo_caixa    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_vendas   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_calculado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aberto_em      = models.DateTimeField(auto_now_add=True)
    fechado_em     = models.DateTimeField(null=True, blank=True)
    criado_por     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='caixas_criados')
    class Meta:
        db_table = 'pdv_sessao_caixa'
        ordering = ['-aberto_em']
    def __str__(self): return f'Caixa #{self.pk} — {self.operador.nome}'

class VendaPDV(models.Model):
    sessao           = models.ForeignKey(SessaoCaixa, on_delete=models.PROTECT, related_name='vendas')
    operador         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='vendas_operador')
    cliente          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendas_cliente')
    tipo             = models.CharField(max_length=10, choices=[('venda','Venda'),('orcamento','Orçamento')], default='venda')
    status           = models.CharField(max_length=10, choices=StatusVenda.CHOICES, default=StatusVenda.ABERTA)
    subtotal         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desconto_valor   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pontos_gerados   = models.IntegerField(default=0)
    observacao       = models.TextField(blank=True, null=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    finalizada_em    = models.DateTimeField(null=True, blank=True)
    criado_por       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='vendas_criadas')
    atualizado_por   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendas_atualizadas')
    class Meta:
        db_table = 'pdv_venda'
        ordering = ['-criado_em']
    def __str__(self): return f'Venda #{self.pk} — R${self.total}'

class ItemVenda(models.Model):
    venda          = models.ForeignKey(VendaPDV, on_delete=models.CASCADE, related_name='itens')
    produto        = models.ForeignKey('products.Produto', on_delete=models.PROTECT, related_name='itens_venda')
    quantidade     = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto_item  = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    total          = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = 'pdv_item_venda'
    def __str__(self): return f'{self.produto.nome} x {self.quantidade}'

class PagamentoPDV(models.Model):
    venda           = models.ForeignKey(VendaPDV, on_delete=models.CASCADE, related_name='pagamentos')
    forma_pagamento = models.CharField(max_length=20, choices=FormaPagamento.CHOICES)
    valor           = models.DecimalField(max_digits=12, decimal_places=2)
    troco           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em       = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'pdv_pagamento'
    def get_forma_pagamento_display(self):
        return dict(FormaPagamento.CHOICES).get(self.forma_pagamento, self.forma_pagamento)
    def __str__(self): return f'{self.get_forma_pagamento_display()} — R${self.valor}'
