from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.views import (
    LoginView, LogoutView, MeuPerfilView,
    UserListCreateView, UserDetailView,
    ClienteListCreateView, ClienteDetailView, ClientePontosView,
)
urlpatterns = [
    path('login/',                    LoginView.as_view(),           name='login'),
    path('logout/',                   LogoutView.as_view(),          name='logout'),
    path('refresh/',                  TokenRefreshView.as_view(),    name='token-refresh'),
    path('me/',                       MeuPerfilView.as_view(),       name='me'),
    path('users/',                    UserListCreateView.as_view(),  name='user-list-create'),
    path('users/<int:pk>/',           UserDetailView.as_view(),      name='user-detail'),
    path('clients/',                  ClienteListCreateView.as_view(), name='cliente-list-create'),
    path('clients/<int:pk>/',         ClienteDetailView.as_view(),   name='cliente-detail'),
    path('clients/<int:pk>/pontos/',  ClientePontosView.as_view(),   name='cliente-pontos'),
]
