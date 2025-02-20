from flask import Flask
from database import db

app = Flask(__name__)

app.config['SECRET_KEY'] = "FLASK_SECRET_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5434/estoque_daily_diet"

db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)