class PerfilUsuario:
    ADMINISTRADOR = 'administrador'
    FUNCIONARIO   = 'funcionario'
    CLIENTE       = 'cliente'
    CHOICES = [('administrador','Administrador'),('funcionario','Funcionário'),('cliente','Cliente')]

class StatusEstoque:
    NORMAL  = 'normal'
    BAIXO   = 'baixo'
    ZERADO  = 'zerado'
    CHOICES = [('normal','Normal'),('baixo','Estoque Baixo'),('zerado','Zerado')]

class UnidadeMedida:
    UNIDADE = 'un'; CAIXA = 'cx'; PACOTE = 'pct'
    KG = 'kg'; GRAMA = 'g'; LITRO = 'l'; ML = 'ml'; METRO = 'm'
    INTEIRAS = ['un', 'cx', 'pct']
    CHOICES = [
        ('un','Unidade (un)'),('cx','Caixa (cx)'),('pct','Pacote (pct)'),
        ('kg','Quilograma (kg)'),('g','Grama (g)'),
        ('l','Litro (l)'),('ml','Mililitro (ml)'),('m','Metro (m)'),
    ]

class FormaPagamento:
    DINHEIRO = 'dinheiro'; CARTAO_DEB = 'cartao_debito'
    CARTAO_CRED = 'cartao_credito'; PIX = 'pix'; PONTOS = 'pontos'
    CHOICES = [
        ('dinheiro','Dinheiro'),('cartao_debito','Cartão de Débito'),
        ('cartao_credito','Cartão de Crédito'),('pix','PIX'),('pontos','Pontos'),
    ]

class StatusVenda:
    ABERTA    = 'aberta'
    CONCLUIDA = 'concluida'
    CANCELADA = 'cancelada'
    CHOICES   = [('aberta','Aberta'),('concluida','Concluída'),('cancelada','Cancelada')]

class StatusCaixa:
    ABERTO  = 'aberto'
    FECHADO = 'fechado'
    CHOICES = [('aberto','Aberto'),('fechado','Fechado')]

class StatusOrcamento:
    ABERTO     = 'aberto'
    APROVADO   = 'aprovado'
    RECUSADO   = 'recusado'
    CONVERTIDO = 'convertido'
    EXPIRADO   = 'expirado'
    CHOICES = [
        ('aberto','Aberto'),('aprovado','Aprovado'),('recusado','Recusado'),
        ('convertido','Convertido'),('expirado','Expirado'),
    ]

class StatusNota:
    EMITIDA   = 'emitida'
    CANCELADA = 'cancelada'
    CHOICES   = [('emitida','Emitida'),('cancelada','Cancelada')]

class TipoPontos:
    CREDITO  = 'credito'
    DEBITO   = 'debito'
    VOUCHER  = 'voucher'
    ESTORNO  = 'estorno'
    CHOICES  = [('credito','Crédito'),('debito','Débito'),('voucher','Voucher'),('estorno','Estorno')]
