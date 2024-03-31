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
            return "Error"
        
        user_login.insert_one(user)
        return "Success"
    
    def login(self, username, password):
        #* prevent HTML injection
        username = username.replace('&', "&amp")
        username = username.replace('<', "&lt")
        username = username.replace('>', "&gt")

        user = user_login.find_one({"username": username})

        if user:
            if user["password"] == bcrypt.hashpw(password.encode("utf-8"), user["salt"]):
                authToken = secrets.token_hex(20) 
                hashedAuth = hashlib.new('sha256')
                hashedAuth.update(authToken.encode())
                hashedAuth = hashedAuth.hexdigest()
                user_login.update_one({"username":username}, {"$set":{"authHash":hashedAuth}})

                return authToken
            else:
                return "Invalid username/password"
        else:
            return "Invalid username/password"
    
    def logout(self, token):
        hashedAuth = hashlib.new('sha256')
        hashedAuth.update(token.encode())
        hashedAuth = hashedAuth.hexdigest()

        if user_login.find_one({"authHash": hashedAuth}):
            user_login.update_one({"authHash": hashedAuth}, {"$unset":{"authHash":""}})
            return "Logged Out"
        else:
            return "Error"
        
    def checkLoggedIn(self, token):
        hashedAuth = hashlib.new('sha256')
        hashedAuth.update(token.encode())
        hashedAuth = hashedAuth.hexdigest()

        foundUser = user_login.find_one({"authHash": hashedAuth})
        if foundUser:
            return foundUser
        else:
            return None

