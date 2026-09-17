from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from gestao import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", auth_views.LoginView.as_view(), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("painel/", views.painel, name="painel"),

    path("associados/", views.AssociadoLista.as_view(), name="associados"),
    path("associados/novo/", views.AssociadoNovo.as_view(), name="associado_novo"),
    path("associados/<int:pk>/editar/", views.AssociadoEditar.as_view(), name="associado_editar"),
    path("associados/<int:pk>/excluir/", views.AssociadoExcluir.as_view(), name="associado_excluir"),

    path("financeiro/", views.LancamentoLista.as_view(), name="financeiro"),
    path("financeiro/novo/", views.LancamentoNovo.as_view(), name="lancamento_novo"),
    path("financeiro/<int:pk>/editar/", views.LancamentoEditar.as_view(), name="lancamento_editar"),
    path("financeiro/<int:pk>/excluir/", views.LancamentoExcluir.as_view(), name="lancamento_excluir"),

    path("avisos/", views.AvisoLista.as_view(), name="avisos"),
    path("avisos/novo/", views.AvisoNovo.as_view(), name="aviso_novo"),
    path("avisos/<int:pk>/editar/", views.AvisoEditar.as_view(), name="aviso_editar"),
    path("avisos/<int:pk>/excluir/", views.AvisoExcluir.as_view(), name="aviso_excluir"),

    path("admin/", admin.site.urls),
]
