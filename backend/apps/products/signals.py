from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import Produto
from apps.core.choices import StatusEstoque

@receiver(post_save, sender=Produto)
def verificar_estoque(sender, instance, **kwargs):
    if kwargs.get('update_fields') and 'status_estoque' in kwargs['update_fields']:
        return
    novo = StatusEstoque.ZERADO if instance.quantidade_estoque <= 0 \
           else StatusEstoque.BAIXO if instance.quantidade_estoque <= instance.estoque_minimo \
           else StatusEstoque.NORMAL
    if novo != instance.status_estoque:
        Produto.objects.filter(pk=instance.pk).update(status_estoque=novo)
