from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
user_login = db["user_login"]