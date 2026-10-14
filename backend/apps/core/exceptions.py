from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            detail = response.data.get('detail', response.data)
        else:
            detail = response.data
        response.data = {'erro': True, 'status': response.status_code,
                         'mensagem': str(detail), 'detalhes': response.data}
    return response

class EstoqueInsuficienteError(Exception):
    def __init__(self, produto='', disponivel=0, solicitado=0):
        super().__init__(f"Estoque insuficiente: '{produto}'. Disponível: {disponivel}, Solicitado: {solicitado}.")

class CaixaFechadoError(Exception):
    def __init__(self): super().__init__('Nenhum caixa aberto. Abra o caixa antes de operar.')

class CaixaJaAbertoError(Exception):
    def __init__(self): super().__init__('Já existe um caixa aberto para este operador.')

class PontosInsuficientesError(Exception):
    def __init__(self, saldo=0, solicitado=0):
        super().__init__(f"Pontos insuficientes. Saldo: {saldo}, Solicitado: {solicitado}.")
