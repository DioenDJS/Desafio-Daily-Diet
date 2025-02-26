from models.models import Snack, user_snack
from database import db
from typing import Any
from datetime import datetime
from sqlalchemy.orm import joinedload

class DataBase():
    def select_all_snacks(user_id):
        return db.session.query(Snack).join(user_snack).filter(user_snack.c.user_id == user_id).all()

    def select_snack_data(user_id, start_date, end_date):
        return db.session.query(Snack).join(user_snack).filter(
            user_snack.c.user_id == user_id,
            Snack.date >= start_date,
            Snack.date <= end_date
        ).options(joinedload(Snack.user)).all()

    def select_snack_for_name(user_id, snack_name):
        return db.session.query(Snack).join(user_snack).filter(
            user_snack.c.user_id == user_id,
            Snack.name == snack_name
        ).first()

    def select_snack_for_id(user_id, snack_id):
        return db.session.query(Snack).join(user_snack).filter(
            user_snack.c.user_id == user_id,
            Snack.id == snack_id
        ).first()

    def search_snack_for_name(user_id, snack_name):
        return db.session.query(Snack).join(user_snack).filter(
            user_snack.c.user_id == user_id,
            Snack.name.ilike(f"%{snack_name}%")
        ).all()

    def deleted(obj: Any) -> bool:
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception as e:
            print(str(e))



