from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from servicos.database.manager import DatabaseManager

cadastro_bp = Blueprint("cadastro", __name__)

@cadastro_bp.route("/cadastro", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        cpf = request.form.get("cpf", "").strip()
        nome = request.form.get("nome", "").strip()
        endereco = request.form.get("endereco", "").strip()
        senha = request.form.get("senha", "")
        # Usa getlist para capturar todos os checkboxes marcados com name="perfil"
        perfis = request.form.getlist("perfil")

        if not cpf or not nome or not senha:
            flash("Preencha os campos obrigatórios (CPF, Nome e Senha).")
            return redirect(url_for("cadastro.registrar"))
            
        if not perfis:
            flash("Selecione pelo menos um tipo de funcionário.")
            return redirect(url_for("cadastro.registrar"))

        senha_hash = generate_password_hash(senha)
        db = DatabaseManager()

        try:
            # 1. Verifica se CPF já existe
            usuario_existente = db.execute_select_one("SELECT cpf FROM funcionario WHERE cpf = %s", (cpf,))
            if usuario_existente:
                flash("CPF já cadastrado.")
                return redirect(url_for("cadastro.registrar"))

            # 2. Prepara a lista de operações para a transação
            operacoes = []

            # Adiciona o INSERT na tabela principal
            query_func = """
                INSERT INTO funcionario (cpf, nome, endereco, senha_hash, ativo) 
                VALUES (%s, %s, %s, %s, TRUE)
            """
            operacoes.append((query_func, (cpf, nome, endereco, senha_hash)))
            
            # Adiciona os INSERTs nas subclasses dependendo dos checkboxes marcados
            for perfil in perfis:
                if perfil == "COORDENADOR":
                    operacoes.append(("INSERT INTO coordenador (cpf_funcionario) VALUES (%s)", (cpf,)))
                elif perfil == "PROFESSOR":
                    operacoes.append(("INSERT INTO professor (cpf_funcionario) VALUES (%s)", (cpf,)))
                elif perfil == "RECREADOR":
                    operacoes.append(("INSERT INTO recreador (cpf_funcionario) VALUES (%s)", (cpf,)))
            
            # 3. Executa tudo de uma vez. Se falhar no meio, nada é salvo.
            db.execute_transaction(operacoes)
            
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash(f"Erro ao cadastrar: Verifique os dados inseridos.")
            return redirect(url_for("cadastro.registrar"))
            
        finally:
            db.close()

    return render_template("pages/cadastro/cadastro.html")