from flask import Blueprint, jsonify, request

from servicos.livros import LivrosDatabase


livros_blueprint = Blueprint("livro", __name__)


@livros_blueprint.route("/livros", methods=["GET"])
def get_livros():
    rg = request.args.get("rg", "")
    editora = request.args.get("editora", "")
    livro = request.args.get("livro", "")
    return jsonify(LivrosDatabase().get_livros(rg, editora, livro)), 200
