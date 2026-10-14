from django.db import models
from django.conf import settings
from apps.core.choices import TipoPontos

class ExtratoPontos(models.Model):
    cliente    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='extrato_pontos')
    tipo       = models.CharField(max_length=10, choices=TipoPontos.CHOICES)
    pontos     = models.IntegerField()
    saldo_apos = models.IntegerField()
    descricao  = models.CharField(max_length=255)
    venda      = models.ForeignKey('pdv.VendaPDV', on_delete=models.SET_NULL, null=True, blank=True)
    criado_em  = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'loyalty_extrato'
        ordering = ['-criado_em']
    def __str__(self): return f'{self.cliente.nome} — {self.tipo} — {self.pontos}pts'
    def get_tipo_display(self): return dict(TipoPontos.CHOICES).get(self.tipo, self.tipo)
