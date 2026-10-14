from django.urls import path
from apps.loyalty.views import ExtratoView, RankingView
urlpatterns = [
    path('extrato/<int:cliente_id>/', ExtratoView.as_view(), name='loyalty-extrato'),
    path('ranking/',                  RankingView.as_view(), name='loyalty-ranking'),
]
