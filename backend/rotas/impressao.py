from flask import Blueprint, jsonify, request

from servicos.impressao import ImpressaoDatabase


impressao_blueprint = Blueprint("impressao", __name__)


@impressao_blueprint.route("/impressos", methods=["GET"])
def get_impressos():
    return jsonify(ImpressaoDatabase().get_impressos()), 200


@impressao_blueprint.route("/impressos", methods=["POST"])
def post_impressao():
    json = request.get_json()
    data = json.get("data")
    isbn = json.get("isbn")
    grafica_id = json.get("grafica")
    nto_copias = json.get("copias")
    registro = ImpressaoDatabase().regristra_impressao(
        isbn, grafica_id, nto_copias, data
    )

    if not registro:
        return jsonify("Não foi possível solicitar a impressão"), 400

    return jsonify("Impressao requisitada"), 200
