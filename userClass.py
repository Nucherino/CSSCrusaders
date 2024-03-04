from flask import Flask, jsonify, flask_bcrypt
import uuid
from passlib.hash import pbkdf2_sha256
from server import user_login


class User:

    def signup(self, username, password):
        saltRounds = 10
        user = {
            "_id": uuid.uuid4().hex,
            "username": username,
            "password": password,
            "hash": pbkdf2_sha256.hash()
        }
        user["password"] = pbkdf2_sha256.using(rounds=8000, salt_size=10).hash(user["password"])
        if user_login.find_one({"username", user["username"]}):
            return jsonify({"Error": "Username already exists"}), 400
        user_login.insert_one(user)
        return jsonify(user), 200
