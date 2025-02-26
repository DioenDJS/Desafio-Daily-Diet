from flask import Flask, request, jsonify
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
from sqlalchemy.orm import joinedload

from models.models import User, Snack, user_snack
from database import db
from data import DataBase
import bcrypt
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = "FLASK_SECRET_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5434/estoque_daily_diet"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_name = data.get("username")
    password = data.get("password")

    if user_name and password:
        user = User.query.filter_by(username=user_name).first()
    
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return jsonify({'message': 'Autenticação realizada com sucesso! '}), 200

    return jsonify({'message': "Credenciais inválidas"}), 400

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return jsonify({"message": "Usuario deslogado com sucesso!"})

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    user_name = data.get("username")
    password = data.get("password")

    if user_name and password:
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = hashed_bytes.decode('utf-8')
        user = User(username=user_name, password=hashed_password, role="user")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"})

    return jsonify({"message": "Dados invalidos"}), 400

@app.route("/me", methods=['GET'])
@login_required
def get_me():
    user_id = current_user.id

    user = User.query.get(id=user_id)

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name
        }
    })

@app.route("/snack", methods=["POST"])
@login_required
def create_snack():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date = datetime.now()
    in_diet = data.get("in_diet")

    snack = Snack(name=name, description=description, date=date, in_diet=in_diet)
    snack.users.append(current_user)
    db.session.add(snack)
    db.session.commit()
    return jsonify({"message": "Refeição criada com sucesso"})

@app.route("/snacks", methods=['GET'])
@login_required
def get_all_snacks():
    user_id = current_user.id

    snacks = DataBase.select_all_snacks(user_id)

    return jsonify({
        "snacks": [{
            "name": snack.name,
            "id": snack.id,
            "descrição": snack.description,
            "data": snack.date,
            "Dentro da dieta": "dentro" if snack.in_diet else "fora"
        } for snack in snacks]
    })

@app.route("/snack/name/<name>", methods=['GET'])
@login_required
def get_snack_for_name(name: str):

    user_id = current_user.id

    snack = DataBase.select_snack_for_name(user_id, name)

    if not snack:
        return jsonify({"message": "Refeição não encontrada!"}), 404

    return jsonify({
        "Refeição": {
            "id": snack.id,
            "nome": snack.name,
            "descrição": snack.description,
            "data": snack.date,
            "Dentro da dieta": "dentro" if snack.in_diet else "fora"
        }
    })

@app.route("/snack/id/<snack_id>", methods=['GET'])
@login_required
def get_snack_for_id(snack_id):

    user_id = current_user.id

    print(snack_id)
    snack = DataBase.select_snack_for_id(user_id, snack_id)

    if not snack:
        return jsonify({"message": "Refeição não encontrada!"}), 404

    return jsonify({
        "Refeição": {
            "id": snack.id,
            "nome": snack.name,
            "descrição": snack.description,
            "data": snack.date,
            "Dentro da dieta": "dentro" if snack.in_diet else "fora"
        }
    })

@app.route("/search/snack/<name>", methods=['GET'])
@login_required
def search_snack_for_name(name: str):

    user_id = current_user.id

    snacks = DataBase.search_snack_for_name(user_id, name)

    if not snacks:
        return jsonify({"message": "Refeição não encontrada!"}), 404

    return jsonify({
        "snacks": [{
            "name": snack.name,
            "id": snack.id,
            "descrição": snack.description,
            "data": snack.date,
            "Dentro da dieta": "dentro" if snack.in_diet else "fora"
        } for snack in snacks]
    })

@app.route("/snack/<snack_id>", methods=['DELETE'])
@login_required
def deleted_snack(snack_id):

    user_id = current_user.id

    snack = DataBase.select_snack_for_id(user_id, snack_id)

    if not snack:
        return jsonify({"message": "Refeição não encontrada!"}), 404

    result = DataBase.deleted(snack)

    if not result:
        return jsonify({"message": f"Falha ao tentar deletar a Refeição {snack_id} "})

    return jsonify({"message": f"Refeição {snack_id} deletado com sucesso!"}), 200

@app.route("/snack/<snack_id>", methods=['PUT'])
@login_required
def update_snack(snack_id):
    user_id = current_user.id

    data = request.json
    data_keys = list(data.keys())
    snack = DataBase.select_snack_for_id(user_id, snack_id)

    if not snack:
        return jsonify({"message": f"Refeição {snack_id} não encontrada!"})

    for field_snack in data_keys:
        setattr(snack, field_snack, data.get(field_snack))
    db.session.commit()
    return jsonify({"message": f"Refeição {snack_id} não encontrada!"}), 200



@app.route("/snack/controle_calorias/<date_start>/<date_end>", methods=['GET'])
@login_required
def controal_cal(date_start, date_end):
    user_id = current_user.id

    snacks = DataBase.select_snack_data(user_id, start_date=date_start, end_date=date_end)

    list_ingredients = [snacks.description for snack in snacks]




if __name__ == "__main__":
    app.run(debug=True)