from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AssociadoForm, AvisoForm, LancamentoForm
from .models import Associado, Aviso, Lancamento


def eventos_futuros():
    return Aviso.objects.filter(tipo=Aviso.EVENTO, data_evento__gte=timezone.now()).order_by("data_evento")


def inicio(request):
    """Mural público: qualquer morador consulta avisos e eventos sem precisar de login."""
    return render(request, "gestao/inicio.html", {
        "eventos": eventos_futuros().filter(publicado=True),
        "avisos": Aviso.objects.filter(publicado=True, tipo=Aviso.AVISO)[:10],
    })


@login_required
def painel(request):
    hoje = timezone.localdate()
    return render(request, "gestao/painel.html", {
        "associados_ativos": Associado.objects.filter(ativo=True).count(),
        "mes": Lancamento.resumo(Lancamento.objects.filter(data__year=hoje.year, data__month=hoje.month)),
        "geral": Lancamento.resumo(Lancamento.objects.all()),
        "ultimos": Lancamento.objects.select_related("associado")[:5],
        "eventos": eventos_futuros()[:3],
    })


class Cadastro(LoginRequiredMixin):
    """Base de criar/editar/excluir: título da página, link de voltar e mensagem de confirmação."""

    template_name = "gestao/form.html"
    titulo = ""
    mensagem = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(titulo=self.titulo, voltar=self.success_url, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.mensagem)
        return super().form_valid(form)


class Exclusao(Cadastro, DeleteView):
    template_name = "gestao/confirmar_exclusao.html"


# ---- Associados ----

class AssociadoLista(LoginRequiredMixin, ListView):
    model = Associado
    paginate_by = 25

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = super().get_queryset()
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(telefone__icontains=q) | Q(endereco__icontains=q))
        return qs


class AssociadoNovo(Cadastro, CreateView):
    model = Associado
    form_class = AssociadoForm
    success_url = reverse_lazy("associados")
    titulo = "Novo associado"
    mensagem = "Associado cadastrado."


class AssociadoEditar(Cadastro, UpdateView):
    model = Associado
    form_class = AssociadoForm
    success_url = reverse_lazy("associados")
    titulo = "Editar associado"
    mensagem = "Associado atualizado."


class AssociadoExcluir(Exclusao):
    model = Associado
    success_url = reverse_lazy("associados")
    titulo = "Excluir associado"
    mensagem = "Associado excluído."


# ---- Financeiro ----

class LancamentoLista(LoginRequiredMixin, ListView):
    model = Lancamento

    def mes(self):
        """Mês escolhido em ?mes=AAAA-MM; sem filtro (ou valor inválido), o mês atual."""
        try:
            ano, mes = map(int, self.request.GET["mes"].split("-"))
            return date(ano, mes, 1)
        except (KeyError, ValueError):
            return timezone.localdate().replace(day=1)

    def get_queryset(self):
        m = self.mes()
        return super().get_queryset().select_related("associado").filter(data__year=m.year, data__month=m.month)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mes"] = self.mes()
        ctx["resumo"] = Lancamento.resumo(self.object_list)
        ctx["saldo_geral"] = Lancamento.resumo(Lancamento.objects.all())["saldo"]
        return ctx


class LancamentoNovo(Cadastro, CreateView):
    model = Lancamento
    form_class = LancamentoForm
    success_url = reverse_lazy("financeiro")
    titulo = "Novo lançamento"
    mensagem = "Lançamento registrado."


class LancamentoEditar(Cadastro, UpdateView):
    model = Lancamento
    form_class = LancamentoForm
    success_url = reverse_lazy("financeiro")
    titulo = "Editar lançamento"
    mensagem = "Lançamento atualizado."


class LancamentoExcluir(Exclusao):
    model = Lancamento
    success_url = reverse_lazy("financeiro")
    titulo = "Excluir lançamento"
    mensagem = "Lançamento excluído."


# ---- Avisos e eventos ----

class AvisoLista(LoginRequiredMixin, ListView):
    model = Aviso
    paginate_by = 25


class AvisoNovo(Cadastro, CreateView):
    model = Aviso
    form_class = AvisoForm
    success_url = reverse_lazy("avisos")
    titulo = "Novo aviso ou evento"
    mensagem = "Aviso salvo."


class AvisoEditar(Cadastro, UpdateView):
    model = Aviso
    form_class = AvisoForm
    success_url = reverse_lazy("avisos")
    titulo = "Editar aviso ou evento"
    mensagem = "Aviso atualizado."


class AvisoExcluir(Exclusao):
    model = Aviso
    success_url = reverse_lazy("avisos")
    titulo = "Excluir aviso"
    mensagem = "Aviso excluído."
