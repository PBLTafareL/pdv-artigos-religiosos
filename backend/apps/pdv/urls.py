from django.urls import path
from apps.pdv.views import (
    AbrirCaixaView, CaixaAtualView, FecharCaixaView,
    IniciarVendaView, VendaDetailView, AdicionarItemView, RemoverItemView,
    VincularClienteView, AplicarVoucherView, RegistrarPagamentoView,
    FinalizarVendaView, CancelarVendaView, SalvarOrcamentoView, VendaListView,
)
urlpatterns = [
    path('caixa/abrir/',                       AbrirCaixaView.as_view(),        name='caixa-abrir'),
    path('caixa/atual/',                       CaixaAtualView.as_view(),        name='caixa-atual'),
    path('caixa/<int:sessao_id>/fechar/',      FecharCaixaView.as_view(),       name='caixa-fechar'),
    path('vendas/',                            VendaListView.as_view(),          name='venda-list'),
    path('vendas/iniciar/',                    IniciarVendaView.as_view(),       name='venda-iniciar'),
    path('vendas/<int:venda_id>/',             VendaDetailView.as_view(),        name='venda-detail'),
    path('vendas/<int:venda_id>/itens/',       AdicionarItemView.as_view(),      name='item-add'),
    path('vendas/<int:venda_id>/itens/<int:item_id>/', RemoverItemView.as_view(), name='item-remove'),
    path('vendas/<int:venda_id>/cliente/',     VincularClienteView.as_view(),    name='venda-cliente'),
    path('vendas/<int:venda_id>/voucher/',     AplicarVoucherView.as_view(),     name='venda-voucher'),
    path('vendas/<int:venda_id>/pagamento/',   RegistrarPagamentoView.as_view(), name='venda-pagamento'),
    path('vendas/<int:venda_id>/finalizar/',   FinalizarVendaView.as_view(),     name='venda-finalizar'),
    path('vendas/<int:venda_id>/cancelar/',    CancelarVendaView.as_view(),      name='venda-cancelar'),
    path('vendas/<int:venda_id>/orcamento/',   SalvarOrcamentoView.as_view(),    name='venda-orcamento'),
]
