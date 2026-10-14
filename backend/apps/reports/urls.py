from django.urls import path
from apps.reports.views import RelVendasView, RelProdutosView, RelEstoqueView
urlpatterns = [
    path('vendas/',   RelVendasView.as_view(),   name='rel-vendas'),
    path('produtos/', RelProdutosView.as_view(),  name='rel-produtos'),
    path('estoque/',  RelEstoqueView.as_view(),   name='rel-estoque'),
]
