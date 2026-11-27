from flask import Blueprint, request, jsonify, session
from servicos.consultas import (
    consultar_engajamento_moedas,
    consultar_desempenho_pedagogico,
    consultar_necessidades_contatos,
    consultar_alunos_por_interesse,
    listar_opcoes_interesses,
    consultar_desempenho_recreadores,
    consultar_desempenho_professores,
    consultar_carga_trabalho,
    consultar_desempenho_atividades,
    consultar_disciplinas_oferecimentos,
    consultar_rendimento_individual,
    consultar_distribuicao_moedas,
)

consultas_bp = Blueprint("consultas", __name__, url_prefix="/api/consultas")

#Requisito funcional 1: Consultas sobre desempenho dos alunos
#Domínio 1: Engajamento e moedas
@consultas_bp.route("/engajamento", methods=["GET"])
def rota_engajamento():
    dados = consultar_engajamento_moedas(
        ultimos_meses=request.args.get("ultimos_meses", type=int),
        tipo_impacto=request.args.get("tipo_impacto"),
        top_atividades=request.args.get("top_atividades", type=int),
        ordenar_por=request.args.get("ordenar_por", default="girassois"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200

#Domínio 2: Desempenho pedagogico
@consultas_bp.route("/pedagogico", methods=["GET"])
def rota_pedagogico():
    dados = consultar_desempenho_pedagogico(
        disciplina=request.args.get("disciplina"),
        abaixo_media=request.args.get("abaixo_media", default="false").lower() == "true",
        qtd_disciplinas_abaixo=request.args.get("qtd_disciplinas_abaixo", type=int),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200

#Domínio 3: Necessidades especiais
@consultas_bp.route("/necessidades", methods=["GET"])
def rota_necessidades():
    dados = consultar_necessidades_contatos(
        ordenar_por=request.args.get("ordenar_por", default="contatos"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


#Dominio 4: Interesses
@consultas_bp.route("/interesses/opcoes", methods=["GET"])
def rota_opcoes_interesses():
    dados = listar_opcoes_interesses()
    return jsonify({"total": len(dados), "dados": dados}), 200


@consultas_bp.route("/interesses", methods=["GET"])
def rota_alunos_interesse():
    dados = consultar_alunos_por_interesse(
        interesse=request.args.get("interesse"),
        cod_atividade=request.args.get("cod_atividade"),
        apenas_nao_participantes=request.args.get("apenas_nao_participantes", default="false").lower() == "true",
        ordem=request.args.get("ordem", default="asc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200



#Requisito funcional 2: Consultas sobre desempenho de funcionários
#Domínio 5: Quanto às atividades
@consultas_bp.route("/recreadores", methods=["GET"])
def rota_recreadores():
    # Exemplo de trava usando a session do auth.py (descomente quando for testar logado):
    # if session.get("perfil") != "COORDENADOR":
    #     return jsonify({"erro": "Acesso restrito a coordenadores"}), 403

    dados = consultar_desempenho_recreadores(
        top_girassois=request.args.get("top_girassois", type=int),
        ordenar_por=request.args.get("ordenar_por", default="maior_nota"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200

# Domínio 6: Quanto às aulas (Professores)
@consultas_bp.route("/professores", methods=["GET"])
def rota_professores():
    dados = consultar_desempenho_professores(
        ordenar_por=request.args.get("ordenar_por", default="maior_nota_coordenador"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


# Domínio 7: Quanto à carga de trabalho
@consultas_bp.route("/carga-trabalho", methods=["GET"])
def rota_carga_trabalho():
    dados = consultar_carga_trabalho(
        ultimos_meses=request.args.get("ultimos_meses", type=int),
        perfil=request.args.get("perfil"),
        ordenar_por=request.args.get("ordenar_por", default="atividades"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


#Requisito funcional 3: Atividades e aulas
# Domínio 8: Desempenho e logística das atividades
@consultas_bp.route("/atividades", methods=["GET"])
def rota_atividades():
    dados = consultar_desempenho_atividades(
        ultimos_meses=request.args.get("ultimos_meses", type=int),
        local_atividade=request.args.get("local_atividade"),
        data_inicio=request.args.get("data_inicio"),
        data_fim=request.args.get("data_fim"),
        ordenar_por=request.args.get("ordenar_por", default="participacoes"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


# Domínio 9: Quanto às aulas (Disciplinas e Oferecimentos)
@consultas_bp.route("/disciplinas", methods=["GET"])
def rota_disciplinas():
    dados = consultar_disciplinas_oferecimentos(
        data_inicio=request.args.get("data_inicio"),
        data_fim=request.args.get("data_fim"),
        professor=request.args.get("professor"),
        ordenar_por=request.args.get("ordenar_por", default="media_notas"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


#Requisito funcional 4: Educação financeira
# Domínio 10: Rendimento individual
@consultas_bp.route("/rendimento-individual", methods=["GET"])
def rota_rendimento_individual():
    dados = consultar_rendimento_individual(
        aluno=request.args.get("aluno"),
        ultimos_meses=request.args.get("ultimos_meses", type=int),
        data_inicio=request.args.get("data_inicio"),
        data_fim=request.args.get("data_fim"),
        ordenar_por=request.args.get("ordenar_por", default="total_girassois"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200


# Domínio 11: Distribuição de moedas no projeto
@consultas_bp.route("/distribuicao-moedas", methods=["GET"])
def rota_distribuicao_moedas():
    dados = consultar_distribuicao_moedas(
        ultimos_meses=request.args.get("ultimos_meses", type=int),
        data_inicio=request.args.get("data_inicio"),
        data_fim=request.args.get("data_fim"),
        ordenar_por=request.args.get("ordenar_por", default="total_girassois"),
        ordem=request.args.get("ordem", default="desc"),
        limite=request.args.get("limite", type=int),
    )
    return jsonify({"total": len(dados), "dados": dados}), 200