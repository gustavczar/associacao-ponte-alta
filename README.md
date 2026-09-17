# Sistema de Gestão — Associação de Moradores do Jardim Ponte Alta

Sistema web desenvolvido na **Atividade Extensionista II — Tecnologia Aplicada à Inclusão Digital (Projeto)**, CST em Análise e Desenvolvimento de Sistemas, Centro Universitário Internacional UNINTER.

Aluno: Gustavo Cezar Lourenço — RU 4515373
Setor de aplicação: Associação de Moradores do Jardim Ponte Alta, Américo Brasiliense/SP
ODS: 9 (Indústria, inovação e infraestrutura), 10 (Redução das desigualdades), 11 (Cidades e comunidades sustentáveis)

## O que o sistema faz

| Módulo | Quem usa | Funções |
|---|---|---|
| Mural do bairro | Qualquer morador, sem login | Consulta avisos e próximos eventos publicados |
| Associados | Diretoria | Cadastrar, buscar, editar, inativar e excluir associados |
| Caixa | Diretoria | Registrar entradas e saídas, ver o saldo e o resumo de cada mês |
| Avisos e eventos | Diretoria | Escrever avisos, marcar eventos, publicar ou deixar como rascunho |

## Acessibilidade e inclusão digital

O público é uma diretoria com pouca familiaridade digital, usando principalmente o celular. Por isso:

- a interface usa a forma do **carnê de mensalidade** (campos em caixinhas rotuladas, lançamentos como canhotos), que o público já conhece do papel;
- a fonte é a **Atkinson Hyperlegible**, desenhada para leitores com baixa visão; o botão **A+** aumenta toda a letra e lembra a escolha no aparelho;
- botões e campos têm no mínimo 48 px de altura, com rótulos sempre visíveis;
- navegação por abas fixas embaixo no celular, com ícone e texto;
- mensagens de erro dizem o problema e como resolver; exclusão sempre pede confirmação;
- contraste de cores WCAG AA, foco de teclado visível, link "Pular para o conteúdo".

## Tecnologias

- Python 3.13 e Django 5.2
- PostgreSQL 17
- HTML5, CSS3 e JavaScript (sem frameworks de front-end)
- Docker Compose para subir banco e aplicação juntos

## Como executar

Com Docker instalado:

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Acesse http://localhost:8000 (mural público) e http://localhost:8000/entrar/ (diretoria).

Sem Docker, para desenvolvimento (usa SQLite):

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Testes

```bash
python manage.py test gestao
```

Os 11 testes automatizados cobrem: mural público mostra só o que foi publicado; áreas da diretoria exigem login; cadastro e busca de associados; cálculo do saldo; filtro do caixa por mês; recusa de valor zero; evento sem data; exclusão só após confirmação; histórico do caixa preservado ao excluir um associado.

## Estrutura

```
config/            configurações e rotas do Django
gestao/models.py   Associado, Lancamento, Aviso
gestao/views.py    telas (mural, painel, cadastros)
gestao/forms.py    formulários e validações
gestao/templates/  páginas HTML
gestao/static/     CSS e JavaScript
gestao/tests.py    testes automatizados
```
