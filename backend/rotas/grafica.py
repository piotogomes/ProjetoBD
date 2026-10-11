from flask import Blueprint, jsonify, request

from servicos.grafica import GraficaDatabase


grafica_blueprint = Blueprint("grafica", __name__)


@grafica_blueprint.route("/grafica", methods=["GET"])
def get_graficas():
    return jsonify(GraficaDatabase().get_grafica()), 200
