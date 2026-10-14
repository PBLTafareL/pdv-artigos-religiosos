from django.db import models
from django.conf import settings
from apps.core.models import ModeloBase
from apps.core.choices import StatusNota

class NotaFiscal(ModeloBase):
    numero       = models.CharField(max_length=20, unique=True)
    venda        = models.OneToOneField('pdv.VendaPDV', on_delete=models.PROTECT, related_name='nota_fiscal')
    cliente      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_fiscais')
    status       = models.CharField(max_length=10, choices=StatusNota.CHOICES, default=StatusNota.EMITIDA)
    total        = models.DecimalField(max_digits=12, decimal_places=2)
    arquivo_pdf  = models.FileField(upload_to='notas_fiscais/', null=True, blank=True)
    emitida_em   = models.DateTimeField(auto_now_add=True)
    cancelada_em = models.DateTimeField(null=True, blank=True)
    motivo_cancelamento = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'invoices_nota_fiscal'
        ordering = ['-emitida_em']
    def __str__(self): return f'NF {self.numero}'
    def get_status_display(self): return dict(StatusNota.CHOICES).get(self.status, self.status)
