
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



# ROTA INICIAL
@app.route("/")
def index():

    return redirect(url_for("auth.login"))


# HOME ÚNICA
@app.route("/home")
@login_required
def home():

    return render_template("pages/home/home.html")


# EXEMPLO: SOMENTE COORDENADOR
@app.route("/funcionarios")
@perfil_required("COORDENADOR")
def funcionarios():

    return "Página de funcionários"


# EXEMPLO: COORDENADOR E PROFESSOR
@app.route("/disciplinas")
@perfil_required("COORDENADOR", "PROFESSOR")
def disciplinas():

    return "Página de disciplinas"


# EXEMPLO: COORDENADOR E RECREADOR
@app.route("/atividades")
@perfil_required("COORDENADOR", "RECREADOR")
def atividades():

    return "Página de atividades"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
