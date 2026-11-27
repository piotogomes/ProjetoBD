from flask import Blueprint, request, jsonify, session
from servicos.consultas import (
    consultar_engajamento_moedas,
    consultar_desempenho_pedagogico,
    consultar_desempenho_recreadores,
    consultar_necessidades_contatos,
    consultar_alunos_por_interesse,
    listar_opcoes_interesses,
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
#Domínio 1: Quanto às atividades
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