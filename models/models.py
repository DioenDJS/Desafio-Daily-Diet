import uuid
from database import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

# Tabela de associação entre Usuário e Snack
user_snack = db.Table(
    "user_snack",
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("user.id"), primary_key=True),
    db.Column("snack_id", UUID(as_uuid=True), db.ForeignKey("snack.id"), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String(180), unique=True, nullable=False)
    password = db.Column(db.String(180), nullable=True)
    role = db.Column(db.String(80), nullable=True, default='user')
    snacks = db.relationship("Snack", secondary=user_snack, back_populates="users")

class Snack(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(150), unique=True)
    date = db.Column(db.DateTime, nullable=False)
    in_diet = db.Column(db.Boolean, nullable=False)
    users = db.relationship("User", secondary=user_snack, back_populates="snacks")
