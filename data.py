from models.models import Snack, user_snack
from database import db

class DataBase():
    def select_all_snacks(user_id):
        return db.session.query(Snack).join(user_snack).filter(user_snack.c.user_id == user_id).all()

    def select_snack(user_id, snack_name):
        return db.session.query(Snack).join(user_snack).filter(
            user_snack.c.user_id == user_id,
            Snack.name == snack_name
        ).first()

