
import os

from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect

from servicos.auth import (
    auth_bp,
    login_required,
    perfil_required
)

from servicos.cadastro import (
    cadastro_bp,
)

from rotas.consultas import (
    consultas_bp,
)


frontend_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../frontend"
    )
)


app = Flask(
    __name__,
    template_folder=frontend_path,
    static_folder=frontend_path,
    static_url_path=""
)


# Configurações
app.config["SECRET_KEY"] = "SECRET_KEY"

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Para desenvolvimento local em HTTP.
# Em produção, utilize HTTPS e configure como True.
app.config["SESSION_COOKIE_SECURE"] = False


# Proteção CSRF
csrf = CSRFProtect(app)


# Registro das rotas de autenticação
app.register_blueprint(auth_bp)
app.register_blueprint(cadastro_bp)
app.register_blueprint(consultas_bp)



# ROTA INICIAL
@app.route("/")
def index():

    return redirect(url_for("auth.login"))


# HOME ÚNICA
@app.route("/home")
@login_required
def home():

    return render_template("pages/home/home.html", active_page="home")


# REQUISITO 1: EVOLUÇÃO DO ALUNO (Coordenadores, Professores e Recreadores)
@app.route("/evolucao-aluno")
@perfil_required("COORDENADOR", "PROFESSOR", "RECREADOR")
def evolucao_aluno():

    return render_template(
        "pages/evolucao_aluno/evolucao_aluno.html",
        active_page="evolucao_aluno"
    )


# REQUISITO 2: DESEMPENHO DE FUNCIONÁRIOS (Somente Coordenador)
@app.route("/funcionarios")
@perfil_required("COORDENADOR")
def funcionarios():

    return render_template(
        "pages/funcionarios/funcionarios.html",
        active_page="funcionarios"
    )


# REQUISITO 3: ATIVIDADES E AULAS (Coordenadores, Professores e Recreadores)
@app.route("/atividades-aulas")
@perfil_required("COORDENADOR", "PROFESSOR", "RECREADOR")
def atividades_aulas():

    return render_template(
        "pages/atividades_aulas/atividades_aulas.html",
        active_page="atividades_aulas"
    )


# REQUISITO 4: EDUCAÇÃO FINANCEIRA (Coordenadores e Recreadores)
@app.route("/educacao-financeira")
@perfil_required("COORDENADOR", "RECREADOR")
def educacao_financeira():

    return render_template(
        "pages/educacao_financeira/educacao_financeira.html",
        active_page="educacao_financeira"
    )


# Rotas legadas redirecionam para Atividades e Aulas
@app.route("/disciplinas")
@perfil_required("COORDENADOR", "PROFESSOR")
def disciplinas():

    return redirect(url_for("atividades_aulas"))


@app.route("/atividades")
@perfil_required("COORDENADOR", "RECREADOR")
def atividades():

    return redirect(url_for("atividades_aulas"))


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
