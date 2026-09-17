from django.contrib import admin

from .models import Associado, Aviso, Lancamento

admin.site.register([Associado, Aviso, Lancamento])
