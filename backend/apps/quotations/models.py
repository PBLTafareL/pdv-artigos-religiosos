from django.db import models
from django.conf import settings
from apps.core.models import ModeloBase
from apps.core.choices import StatusOrcamento

class Orcamento(ModeloBase):
    numero       = models.CharField(max_length=20, unique=True)
    cliente      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orcamentos')
    responsavel  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orcamentos_responsavel')
    status       = models.CharField(max_length=15, choices=StatusOrcamento.CHOICES, default=StatusOrcamento.ABERTO)
    validade     = models.DateField()
    subtotal     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desconto_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observacao   = models.TextField(blank=True, null=True)
    venda_pdv    = models.OneToOneField('pdv.VendaPDV', on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamento_origem')
    aprovado_em  = models.DateTimeField(null=True, blank=True)
    recusado_em  = models.DateTimeField(null=True, blank=True)
    motivo_recusa = models.TextField(null=True, blank=True)
    convertido_em = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'quotations_orcamento'
        ordering = ['-criado_em']
    def __str__(self): return f'Orçamento {self.numero}'
    def get_status_display(self): return dict(StatusOrcamento.CHOICES).get(self.status, self.status)
    @property
    def esta_expirado(self):
        from django.utils import timezone
        return self.status == StatusOrcamento.ABERTO and self.validade < timezone.now().date()

class ItemOrcamento(models.Model):
    orcamento      = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    produto        = models.ForeignKey('products.Produto', on_delete=models.PROTECT)
    quantidade     = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total          = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = 'quotations_item'
