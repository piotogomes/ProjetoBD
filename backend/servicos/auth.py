from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort
)
from werkzeug.security import check_password_hash
from functools import wraps
from servicos.database.manager import DatabaseManager

auth_bp = Blueprint("auth", __name__)

# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Se já estiver autenticado, vai para home
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        cpf = request.form.get("cpf", "").strip()
        senha = request.form.get("senha", "")

        if not cpf or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("auth.login"))

        db = DatabaseManager()
        try:
            funcionario = db.execute_select_one(
                """
                SELECT
                    f.cpf,
                    f.nome,
                    f.senha_hash,
                    f.ativo,
                    CASE
                        WHEN c.cpf_funcionario IS NOT NULL THEN 'COORDENADOR'
                        WHEN p.cpf_funcionario IS NOT NULL THEN 'PROFESSOR'
                        WHEN r.cpf_funcionario IS NOT NULL THEN 'RECREADOR'
                    END AS perfil
                FROM funcionario f
                LEFT JOIN coordenador c ON c.cpf_funcionario = f.cpf
                LEFT JOIN professor p ON p.cpf_funcionario = f.cpf
                LEFT JOIN recreador r ON r.cpf_funcionario = f.cpf
                WHERE f.cpf = %s
                """,
                (cpf,)
            )

            # Validações de acesso (dentro do try, mas antes de fechar o DB ou redirecionar)
            if not funcionario or not funcionario["ativo"]:
                flash("CPF ou senha incorretos.")
                return redirect(url_for("auth.login"))
            
            if not check_password_hash(funcionario["senha_hash"], senha):
                flash("CPF ou senha incorretos.")
                return redirect(url_for("auth.login"))
            
            if funcionario["perfil"] not in ("COORDENADOR", "PROFESSOR", "RECREADOR"):
                flash("Funcionário sem perfil válido.")
                return redirect(url_for("auth.login"))
            
            # Autenticação bem-sucedida
            session.clear()
            session["user_id"] = funcionario["cpf"]
            session["cpf"] = funcionario["cpf"]
            session["user_name"] = funcionario["nome"]
            session["perfil"] = funcionario["perfil"]

            return redirect(url_for("home"))

        finally:
            # O finally garante que o banco feche, independentemente de retornos ou erros no try
            db.close()

    # Retorno padrão para o método GET
    return render_template("pages/login/login.html")


# LOGOUT
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# EXIGE LOGIN
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


# EXIGE UM PERFIL ESPECÍFICO
def perfil_required(*perfis_permitidos):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            perfil_usuario = session.get("perfil")
            if perfil_usuario not in perfis_permitidos:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator