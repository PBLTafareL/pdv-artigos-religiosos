from django.urls import path
from apps.products.views import (
    CategoriaListCreateView, CategoriaDetailView,
    ProdutoListCreateView, ProdutoDetailView,
    ProdutoPDVSearchView, AlertasEstoqueView, GerarBarcodeView,
)
urlpatterns = [
    path('categories/',          CategoriaListCreateView.as_view(), name='categoria-list-create'),
    path('categories/<int:pk>/', CategoriaDetailView.as_view(),     name='categoria-detail'),
    path('',                     ProdutoListCreateView.as_view(),   name='produto-list-create'),
    path('pdv-search/',          ProdutoPDVSearchView.as_view(),    name='produto-pdv-search'),
    path('alerts/',              AlertasEstoqueView.as_view(),      name='produto-alerts'),
    path('<int:pk>/',            ProdutoDetailView.as_view(),       name='produto-detail'),
    path('<int:pk>/barcode/',    GerarBarcodeView.as_view(),        name='produto-barcode'),
]
