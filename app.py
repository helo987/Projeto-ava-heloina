from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
from datetime import date
import os
import secrets

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave-temporaria")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)


class Romaneio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identificacao_animal = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(50), nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)
    data_pesagem = db.Column(db.Date, nullable=False, default=date.today)
    observacoes = db.Column(db.String(300))


with app.app_context():
    db.create_all()


def login_obrigatorio():
    return "usuario_id" in session


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


def validar_csrf():
    return secrets.compare_digest(
        request.form.get("csrf_token", ""),
        session.get("csrf_token", "")
    )


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not login_obrigatorio():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def dados_romaneio():
    identificacao = request.form.get("identificacao_animal", "").strip()
    raca = request.form.get("raca", "").strip()
    observacoes = request.form.get("observacoes", "").strip()
    peso = request.form.get("peso_kg", "").strip()
    data_pesagem = request.form.get("data_pesagem", "").strip()

    if not identificacao or not raca or not peso or not data_pesagem:
        return None, "Preencha todos os campos obrigatórios."

    try:
        peso = float(peso)
        data_pesagem = date.fromisoformat(data_pesagem)
    except ValueError:
        return None, "Informe peso e data válidos."

    if peso <= 0 or peso > 2000:
        return None, "O peso deve estar entre 0 e 2000 kg."

    if len(identificacao) > 50 or len(raca) > 50 or len(observacoes) > 300:
        return None, "Um dos campos ultrapassou o limite permitido."

    return {
        "identificacao_animal": identificacao,
        "raca": raca,
        "peso_kg": peso,
        "data_pesagem": data_pesagem,
        "observacoes": observacoes
    }, None


@app.route("/")
@login_required
def index():
    romaneios = Romaneio.query.order_by(Romaneio.id.desc()).all()
    peso_total = db.session.query(db.func.coalesce(db.func.sum(Romaneio.peso_kg), 0)).scalar()
    return render_template("index.html", romaneios=romaneios, peso_total=peso_total)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not validar_csrf():
            flash("Sessão inválida. Tente novamente.")
            return redirect(url_for("login"))

        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(nome=nome).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session.clear()
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            csrf_token()
            return redirect(url_for("index"))

        flash("Usuário ou senha incorretos.")

    return render_template("login.html")


@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        if not validar_csrf():
            flash("Sessão inválida. Tente novamente.")
            return redirect(url_for("cadastro_usuario"))

        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        if len(nome) < 3 or len(nome) > 100 or len(senha) < 6:
            flash("Nome inválido ou senha com menos de 6 caracteres.")
            return redirect(url_for("cadastro_usuario"))

        if Usuario.query.filter_by(nome=nome).first():
            flash("Esse usuário já existe.")
            return redirect(url_for("cadastro_usuario"))

        usuario = Usuario(nome=nome, senha=generate_password_hash(senha))
        db.session.add(usuario)
        db.session.commit()

        flash("Usuário cadastrado com sucesso.")
        return redirect(url_for("login"))

    return render_template("login.html", cadastro=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/romaneio/novo", methods=["GET", "POST"])
@login_required
def cadastrar():
    if request.method == "POST":
        if not validar_csrf():
            flash("Sessão inválida. Tente novamente.")
            return redirect(url_for("cadastrar"))

        dados, erro = dados_romaneio()
        if erro:
            flash(erro)
            return render_template("cadastrar.html")

        db.session.add(Romaneio(**dados))
        db.session.commit()
        flash("Pesagem cadastrada com sucesso.")
        return redirect(url_for("index"))

    return render_template("cadastrar.html")


@app.route("/romaneio/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    romaneio = Romaneio.query.get_or_404(id)

    if request.method == "POST":
        if not validar_csrf():
            flash("Sessão inválida. Tente novamente.")
            return redirect(url_for("editar", id=id))

        dados, erro = dados_romaneio()
        if erro:
            flash(erro)
            return render_template("editar.html", romaneio=romaneio)

        for chave, valor in dados.items():
            setattr(romaneio, chave, valor)

        db.session.commit()
        flash("Pesagem atualizada com sucesso.")
        return redirect(url_for("index"))

    return render_template("editar.html", romaneio=romaneio)


@app.route("/romaneio/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    if not validar_csrf():
        flash("Sessão inválida. Tente novamente.")
        return redirect(url_for("index"))

    romaneio = Romaneio.query.get_or_404(id)
    db.session.delete(romaneio)
    db.session.commit()
    flash("Pesagem excluída com sucesso.")
    return redirect(url_for("index"))


@app.route("/api/romaneios", methods=["GET", "POST"])
@login_required
def api_romaneios():
    if request.method == "GET":
        registros = Romaneio.query.order_by(Romaneio.id.desc()).all()
        return jsonify([
            {
                "id": r.id,
                "identificacao_animal": r.identificacao_animal,
                "raca": r.raca,
                "peso_kg": r.peso_kg,
                "data_pesagem": r.data_pesagem.isoformat(),
                "observacoes": r.observacoes
            }
            for r in registros
        ])

    dados = request.get_json(silent=True) or {}
    obrigatorios = ["identificacao_animal", "raca", "peso_kg", "data_pesagem"]
    if any(not dados.get(campo) for campo in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

    try:
        novo = Romaneio(
            identificacao_animal=str(dados["identificacao_animal"]).strip(),
            raca=str(dados["raca"]).strip(),
            peso_kg=float(dados["peso_kg"]),
            data_pesagem=date.fromisoformat(dados["data_pesagem"]),
            observacoes=str(dados.get("observacoes", "")).strip()
        )
        if novo.peso_kg <= 0 or novo.peso_kg > 2000:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"erro": "Dados inválidos."}), 400

    db.session.add(novo)
    db.session.commit()
    return jsonify({"id": novo.id, "mensagem": "Pesagem criada."}), 201


@app.route("/api/romaneios/<int:id>", methods=["GET", "PUT", "DELETE"])
@login_required
def api_romaneio(id):
    romaneio = Romaneio.query.get_or_404(id)

    if request.method == "GET":
        return jsonify({
            "id": romaneio.id,
            "identificacao_animal": romaneio.identificacao_animal,
            "raca": romaneio.raca,
            "peso_kg": romaneio.peso_kg,
            "data_pesagem": romaneio.data_pesagem.isoformat(),
            "observacoes": romaneio.observacoes
        })

    if request.method == "DELETE":
        db.session.delete(romaneio)
        db.session.commit()
        return jsonify({"mensagem": "Pesagem excluída."})

    dados = request.get_json(silent=True) or {}
    try:
        romaneio.identificacao_animal = str(dados["identificacao_animal"]).strip()
        romaneio.raca = str(dados["raca"]).strip()
        romaneio.peso_kg = float(dados["peso_kg"])
        romaneio.data_pesagem = date.fromisoformat(dados["data_pesagem"])
        romaneio.observacoes = str(dados.get("observacoes", "")).strip()
        if romaneio.peso_kg <= 0 or romaneio.peso_kg > 2000:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        db.session.rollback()
        return jsonify({"erro": "Dados inválidos."}), 400

    db.session.commit()
    return jsonify({"mensagem": "Pesagem atualizada."})


@app.errorhandler(404)
def pagina_404(error):
    return render_template("erro.html", codigo=404, mensagem="Página não encontrada."), 404


@app.errorhandler(500)
def pagina_500(error):
    db.session.rollback()
    return render_template("erro.html", codigo=500, mensagem="Erro interno do servidor."), 500


if __name__ == "__main__":
    app.run(debug=True)
