from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
import os, io

def arredondar(valor, casas=2):
    if not isinstance(valor, Decimal): valor = Decimal(str(valor))
    return valor.quantize(Decimal(10)**-casas, rounding=ROUND_HALF_UP)

def formatar_moeda(valor):
    v = arredondar(valor)
    return f"R$ {v:,.2f}".replace(',','X').replace('.',',').replace('X','.')

def calcular_pontos(valor_total):
    ppr = getattr(settings, 'PONTOS_POR_REAL', 1)
    return int(Decimal(str(valor_total)) * Decimal(str(ppr)))

def garantir_pasta(caminho):
    os.makedirs(caminho, exist_ok=True)
    return caminho

def gerar_qrcode_pix(chave_pix, valor=0):
    try:
        import qrcode
        buf = io.BytesIO()
        img = qrcode.make(f"PIX:{chave_pix}:{valor}")
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None
