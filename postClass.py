from pymongo import MongoClient
import database


class Post:
    def __init__(self, postID, username, content, image):
        self.postID = postID
        self.username = username
        self.content = content.replace("&", "").replace("<", "").replace(">", "")
        self.likes = []
        self.image = image

    def save_to_database(self):
        post_dict = {
            "post_id": self.postID,
            "username": self.username,
            "content": self.content,
            "likes": self.likes,
            "image": self.image
        }
        database.posts_collection.insert_one(post_dict)


class PostHandler:
    def __init__(self):
        self.client = database.mongo_client
        self.db = database.db
        self.collection = database.posts_collection
        self.id_collection = database.id_collection
        self.ensure_id_counter_exists()

    def get_likes(self, post_id):
        postFound = self.collection.find_one({"post_id": post_id})
        return len(postFound["likes"])

    def ensure_id_counter_exists(self):
        if self.id_collection.find_one() is None:
            self.id_collection.insert_one({"id": 0})

    def generate_post_id(self):
        id_kv = self.id_collection.find_one()
        post_id = id_kv["id"]
        self.id_collection.update_one({}, {"$inc": {"id": 1}})
        return post_id

    def create_post(self, username, content, image):
        postID = self.generate_post_id()
        post = Post(postID, username, content, image)
        post.save_to_database()

    def get_all_posts(self):
        return list(self.collection.find())

    def get_all_posts_sorted_by_id(self):
        return list(self.collection.find().sort("post_id", -1))

    def like_post(self, post_id, username):
        post = self.collection.find_one({"post_id": post_id})
        post["likes"].append(username)
        self.collection.replace_one({"post_id": post_id}, post)
        return True

    def unlike_post(self, post_id, username):
        post = self.collection.find_one({"post_id": post_id})
        post["likes"].remove(username)
        self.collection.replace_one({"post_id": post_id}, post)
        return False
