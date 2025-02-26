import pytest
from flask import Flask
from app import app, db, User
from flask_login import login_user
import bcrypt

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def new_user(client):
    with app.app_context():
        password = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
        user = User(username="testuser", password=password, role='user')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user():
    password = bcrypt.hashpw(b"adminpass", bcrypt.gensalt()).decode('utf-8')
    admin = User(username="admin", password=password, role='admin')
    db.session.add(admin)
    db.session.commit()
    return admin

def test_create_user(client):
    response = client.post("/user", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert response.json["message"] == "Usuario cadastrado com sucesso"

def test_login(client, new_user):
    response = client.post("/login", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert response.json["message"] == "Autenticação realizada com sucesso"

def test_login_invalid(client):
    response = client.post("/login", json={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 400

def test_get_me_user(client, new_user):
    client.post("/login", json={"username": "testuser", "password": "password123"})
    response = client.get("/me")
    assert response.status_code == 200
    assert response.json["name"] == "testuser"

def test_update_user(client, new_user):
    client.post("/login", json={"username": "testuser", "password": "password123"})
    response = client.put(f"/user/{new_user.id}", json={"password": "newpass123"})
    assert response.status_code == 200
    assert "Usuário" in response.json["message"]

def test_delete_user(client, new_user, admin_user):
    client.post("/login", json={"username": "admin", "password": "adminpass"})
    response = client.delete(f"/user/{new_user.id}")
    assert response.status_code == 200
    assert "deletado com sucesso" in response.json["message"]

def test_get_users_all(client, admin_user):
    client.post("/login", json={"username": "admin", "password": "adminpass"})
    response = client.get("/users")
    assert response.status_code == 200
    assert "users" in response.json