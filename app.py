from flask import Flask, request, jsonify
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
from models.models import User, Snack, user_snack
from database import db

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
if __name__ == "__main__":
    app.run(debug=True)