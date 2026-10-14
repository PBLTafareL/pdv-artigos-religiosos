from django.urls import path
from apps.quotations.views import (
    OrcamentoListView, OrcamentoDetailView, OrcamentoPDFView,
    AprovarOrcamentoView, RecusarOrcamentoView, ConverterOrcamentoView,
)
urlpatterns = [
    path('',                    OrcamentoListView.as_view(),    name='orcamento-list'),
    path('<int:pk>/',           OrcamentoDetailView.as_view(),  name='orcamento-detail'),
    path('<int:pk>/pdf/',       OrcamentoPDFView.as_view(),     name='orcamento-pdf'),
    path('<int:pk>/aprovar/',   AprovarOrcamentoView.as_view(), name='orcamento-aprovar'),
    path('<int:pk>/recusar/',   RecusarOrcamentoView.as_view(), name='orcamento-recusar'),
    path('<int:pk>/converter/', ConverterOrcamentoView.as_view(),name='orcamento-converter'),
]