import os
from flask import Flask, render_template, redirect
from flask_cors import CORS
from rotas.livros import livros_blueprint
from rotas.impressao import impressao_blueprint
from rotas.grafica import grafica_blueprint

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
app = Flask(__name__, template_folder=frontend_path, static_folder=frontend_path, static_url_path='')

CORS(app, origins="*")

@app.route("/", methods=["GET"])
def home():
    return render_template("/pages/home/home.html"), 200


app.register_blueprint(livros_blueprint)
app.register_blueprint(impressao_blueprint)
app.register_blueprint(grafica_blueprint)

app.run("0.0.0.0", port=8000, debug=True)
