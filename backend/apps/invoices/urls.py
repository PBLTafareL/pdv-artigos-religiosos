from django.urls import path
from apps.invoices.views import NotaListView, EmitirNotaView, DownloadNotaView, CancelarNotaView
urlpatterns = [
    path('',                        NotaListView.as_view(),    name='nota-list'),
    path('emitir/<int:venda_id>/',  EmitirNotaView.as_view(),  name='nota-emitir'),
    path('<int:pk>/download/',      DownloadNotaView.as_view(),name='nota-download'),
    path('<int:pk>/cancelar/',      CancelarNotaView.as_view(),name='nota-cancelar'),
]
