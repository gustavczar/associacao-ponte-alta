from django import forms

from .models import Associado, Aviso, Lancamento


class DataInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%d", **kwargs)


class AssociadoForm(forms.ModelForm):
    class Meta:
        model = Associado
        fields = ["nome", "telefone", "email", "endereco", "data_associacao", "ativo", "observacoes"]
        widgets = {
            "data_associacao": DataInput(),
            "telefone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }


class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = ["tipo", "descricao", "categoria", "valor", "data", "associado"]
        widgets = {
            "tipo": forms.RadioSelect,
            "data": DataInput(),
            "valor": forms.NumberInput(attrs={"inputmode": "decimal", "min": "0.01", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo"].choices = Lancamento.TIPOS  # sem a opção vazia "---------"

    def clean_valor(self):
        valor = self.cleaned_data["valor"]
        if valor <= 0:
            raise forms.ValidationError("Informe um valor maior que zero.")
        return valor


class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = ["tipo", "titulo", "texto", "data_evento", "local", "publicado"]
        widgets = {
            "tipo": forms.RadioSelect,
            "texto": forms.Textarea(attrs={"rows": 5}),
            "data_evento": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def clean(self):
        dados = super().clean()
        if dados.get("tipo") == Aviso.EVENTO and not dados.get("data_evento"):
            self.add_error("data_evento", "Todo evento precisa de data e hora.")
        return dados
