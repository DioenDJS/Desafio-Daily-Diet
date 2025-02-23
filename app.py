from flask import Flask, request, jsonify
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
from sqlalchemy.orm import joinedload

from models.models import User, Snack, user_snack
from database import db
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
        # print(str.encode(user.password))
        # print(str.encode(password))

        # if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
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

    user = User.query.options(joinedload(User.snacks)).filter_by(id=user_id).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404  

    return jsonify({
        "snacks": [{
            "name": snack.name,
            "descrição": snack.description,
            "data": snack.date,
            "Dentro da dieta": "dentro" if snack.in_diet else "fora"
        } for snack in user.snacks]
    })


if __name__ == "__main__":
    app.run(debug=True)