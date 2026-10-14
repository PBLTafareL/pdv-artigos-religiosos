from rest_framework import serializers
from apps.products.models import Produto, Categoria
from apps.core.choices import UnidadeMedida

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id','nome','descricao']

class ProdutoListSerializer(serializers.ModelSerializer):
    categoria_nome       = serializers.CharField(source='categoria.nome', read_only=True)
    status_display       = serializers.SerializerMethodField()
    imagem_url           = serializers.SerializerMethodField()
    imagem_barcode_url   = serializers.SerializerMethodField()
    e_inteiro            = serializers.BooleanField(read_only=True)

    def get_status_display(self, obj): return obj.get_status_estoque_display()
    def get_imagem_url(self, obj):
        if obj.imagem:
            request = self.context.get('request')
            if request: return request.build_absolute_uri(obj.imagem.url)
            return obj.imagem.url
        return None
    def get_imagem_barcode_url(self, obj):
        if obj.imagem_codigo_barras:
            request = self.context.get('request')
            if request: return request.build_absolute_uri(obj.imagem_codigo_barras.url)
            return obj.imagem_codigo_barras.url
        return None

    class Meta:
        model = Produto
        fields = ['id','codigo','codigo_barras','nome','categoria','categoria_nome',
                  'preco_venda','quantidade_estoque','estoque_minimo','unidade_medida',
                  'e_inteiro','status_estoque','status_display','imagem_url','imagem_barcode_url']

class ProdutoDetailSerializer(ProdutoListSerializer):
    class Meta(ProdutoListSerializer.Meta):
        fields = ProdutoListSerializer.Meta.fields + ['preco_custo','descricao','criado_em','atualizado_em']

class ProdutoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['codigo','codigo_barras','nome','descricao','categoria',
                  'preco_custo','preco_venda','quantidade_estoque',
                  'estoque_minimo','unidade_medida']
    def validate_codigo(self, v):
        if Produto.objects.filter(codigo=v).exists():
            raise serializers.ValidationError('Código já cadastrado.')
        return v
    def validate_codigo_barras(self, v):
        if v and Produto.objects.filter(codigo_barras=v).exists():
            raise serializers.ValidationError('Código de barras já cadastrado.')
        return v

class ProdutoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['codigo_barras','nome','descricao','categoria',
                  'preco_custo','preco_venda','quantidade_estoque',
                  'estoque_minimo','unidade_medida']
