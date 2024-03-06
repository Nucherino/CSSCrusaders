import bcrypt, secrets, hashlib
from flask import jsonify
from database import user_login

class User:
    def signup(self, username, password):
        #* prevent HTML injection
        username = username.replace('&', "&amp")
        username = username.replace('<', "&lt")
        username = username.replace('>', "&gt")

        user = {
            "username": username, #TODO: make username HTML-injection safe
            "password": password,
        }

        salt = bcrypt.gensalt()
        user["salt"] = salt
        user["password"] = bcrypt.hashpw(password.encode("utf-8"), salt)

        if user_login.find_one({"username": user["username"]}):
            return jsonify({"Error": "Username already exists"})
        
        user_login.insert_one(user)
        return jsonify(user)
    
    def login(self, username, password):
        #* prevent HTML injection
        username = username.replace('&', "&amp")
        username = username.replace('<', "&lt")
        username = username.replace('>', "&gt")

        user = user_login.find_one({"username": username})

        if user:
            if user["password"] == bcrypt.hashpw(password, user["salt"]):
                authToken = secrets.token_hex(20) 
                hashedAuth = hashlib.new('sha256')
                hashedAuth.update(authToken.encode())
                hashedAuth = hashedAuth.hexdigest()

                return authToken
        else:
            return jsonify({"Error": "Invalid username/password"})