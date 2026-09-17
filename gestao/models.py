from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Associado(models.Model):
    nome = models.CharField("nome completo", max_length=150)
    telefone = models.CharField("telefone / WhatsApp", max_length=20, blank=True)
    email = models.EmailField("e-mail", blank=True)
    endereco = models.CharField("endereço", max_length=200, blank=True)
    data_associacao = models.DateField("data de associação", default=timezone.localdate)
    ativo = models.BooleanField("ativo", default=True)
    observacoes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "associados"

    def __str__(self):
        return self.nome


class Lancamento(models.Model):
    ENTRADA = "E"
    SAIDA = "S"
    TIPOS = [(ENTRADA, "Entrada"), (SAIDA, "Saída")]
    CATEGORIAS = [
        ("mensalidade", "Mensalidade"),
        ("doacao", "Doação"),
        ("evento", "Evento"),
        ("manutencao", "Manutenção"),
        ("contas", "Contas (água, luz, internet)"),
        ("outros", "Outros"),
    ]

    tipo = models.CharField(max_length=1, choices=TIPOS)
    descricao = models.CharField("descrição", max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="outros")
    valor = models.DecimalField("valor (R$)", max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.localdate)
    associado = models.ForeignKey(
        Associado, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="associado (opcional)"
    )

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "lançamento"

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.descricao}"

    @staticmethod
    def resumo(queryset):
        """Totais de entradas, saídas e saldo de um conjunto de lançamentos."""
        entradas = queryset.filter(tipo=Lancamento.ENTRADA).aggregate(t=Sum("valor"))["t"] or 0
        saidas = queryset.filter(tipo=Lancamento.SAIDA).aggregate(t=Sum("valor"))["t"] or 0
        return {"entradas": entradas, "saidas": saidas, "saldo": entradas - saidas}


class Aviso(models.Model):
    AVISO = "aviso"
    EVENTO = "evento"
    TIPOS = [(AVISO, "Aviso"), (EVENTO, "Evento")]

    tipo = models.CharField(max_length=10, choices=TIPOS, default=AVISO)
    titulo = models.CharField("título", max_length=150)
    texto = models.TextField()
    data_evento = models.DateTimeField("data e hora do evento", null=True, blank=True)
    local = models.CharField(max_length=150, blank=True)
    publicado = models.BooleanField("publicar no mural", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return self.titulo
