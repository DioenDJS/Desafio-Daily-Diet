from models.models import Snack, user_snack
from database import db

class DataBase():
    def select_all_snacks(user_id):
        return db.session.query(Snack).join(user_snack).filter(user_snack.c.user_id == user_id).all()
