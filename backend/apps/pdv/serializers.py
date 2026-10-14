from rest_framework import serializers
from apps.pdv.models import SessaoCaixa, VendaPDV, ItemVenda, PagamentoPDV
from apps.core.choices import FormaPagamento

# --- Input Serializers ---
class AbrirCaixaSerializer(serializers.Serializer):
    fundo_caixa = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)

class IniciarVendaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['venda','orcamento'], default='venda', required=False)

class AdicionarItemSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=10, decimal_places=3, min_value=0.001)

class PagamentoSerializer(serializers.Serializer):
    forma_pagamento = serializers.ChoiceField(choices=[c[0] for c in FormaPagamento.CHOICES])
    valor           = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    pontos_resgate  = serializers.IntegerField(default=0, required=False, min_value=0)
    chave_pix       = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')

# --- Output Serializers ---
class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome   = serializers.CharField(source='produto.nome',          read_only=True)
    produto_codigo = serializers.CharField(source='produto.codigo',        read_only=True)
    unidade_medida = serializers.CharField(source='produto.unidade_medida', read_only=True)
    e_inteiro      = serializers.BooleanField(source='produto.e_inteiro',   read_only=True)
    class Meta:
        model  = ItemVenda
        fields = ['id','produto','produto_nome','produto_codigo','unidade_medida','e_inteiro',
                  'quantidade','preco_unitario','desconto_item','total']

class PagamentoPDVSerializer(serializers.ModelSerializer):
    forma_display = serializers.SerializerMethodField()
    def get_forma_display(self, obj): return obj.get_forma_pagamento_display()
    class Meta:
        model  = PagamentoPDV
        fields = ['id','forma_pagamento','forma_display','valor','troco','criado_em']

class SessaoCaixaSerializer(serializers.ModelSerializer):
    operador_nome  = serializers.CharField(source='operador.nome', read_only=True)
    status_display = serializers.SerializerMethodField()
    def get_status_display(self, obj): return dict([('aberto','Aberto'),('fechado','Fechado')]).get(obj.status, obj.status)
    class Meta:
        model  = SessaoCaixa
        fields = ['id','operador','operador_nome','status','status_display',
                  'fundo_caixa','total_vendas','saldo_calculado','aberto_em','fechado_em']

class VendaPDVDetailSerializer(serializers.ModelSerializer):
    itens          = ItemVendaSerializer(many=True, read_only=True)
    pagamentos     = PagamentoPDVSerializer(many=True, read_only=True)
    operador_nome  = serializers.CharField(source='operador.nome', read_only=True)
    cliente_nome   = serializers.SerializerMethodField()
    cliente_pontos = serializers.SerializerMethodField()
    cliente_vouchers = serializers.SerializerMethodField()
    cliente_total_compras = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    def get_cliente_nome(self, obj): return obj.cliente.nome if obj.cliente else None
    def get_cliente_pontos(self, obj): return obj.cliente.saldo_pontos if obj.cliente else 0
    def get_cliente_vouchers(self, obj): return obj.cliente.vouchers_disponiveis if obj.cliente else 0
    def get_cliente_total_compras(self, obj): return obj.cliente.total_compras if obj.cliente else 0
    def get_status_display(self, obj): return dict([('aberta','Aberta'),('concluida','Concluída'),('cancelada','Cancelada')]).get(obj.status, obj.status)

    class Meta:
        model  = VendaPDV
        fields = ['id','sessao','operador','operador_nome','cliente','cliente_nome',
                  'cliente_pontos','cliente_vouchers','cliente_total_compras',
                  'tipo','status','status_display','subtotal','desconto_valor','total',
                  'pontos_gerados','observacao','itens','pagamentos','criado_em','finalizada_em']

class VendaPDVListSerializer(serializers.ModelSerializer):
    operador_nome  = serializers.CharField(source='operador.nome', read_only=True)
    cliente_nome   = serializers.SerializerMethodField()
    total_itens    = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    def get_cliente_nome(self, obj): return obj.cliente.nome if obj.cliente else None
    def get_total_itens(self, obj): return obj.itens.count()
    def get_status_display(self, obj): return dict([('aberta','Aberta'),('concluida','Concluída'),('cancelada','Cancelada')]).get(obj.status, obj.status)
    class Meta:
        model  = VendaPDV
        fields = ['id','operador_nome','cliente_nome','tipo','status','status_display',
                  'subtotal','desconto_valor','total','total_itens','pontos_gerados','criado_em','finalizada_em']
