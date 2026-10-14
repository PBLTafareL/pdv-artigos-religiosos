from django.db import models
from django.conf import settings

class ModeloBase(models.Model):
    criado_em      = models.DateTimeField(auto_now_add=True)
    atualizado_em  = models.DateTimeField(auto_now=True)
    criado_por     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='%(class)s_criados')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='%(class)s_atualizados')
    ativo = models.BooleanField(default=True)
    class Meta:
        abstract = True
        ordering = ['-criado_em']
    def deletar(self, usuario=None):
        self.ativo = False
        if usuario: self.atualizado_por = usuario
        self.save()
