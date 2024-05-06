import fleep, os
from flask import Flask, request, make_response, redirect, render_template, send_from_directory, Response, jsonify
from flask_socketio import SocketIO, emit
from database import *
from userClass import *
import mimetypes, hashlib
from postClass import PostHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import time

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/jpg', '.jpg')

app = Flask(__name__, template_folder='public')
UPLOAD_FOLDER = '/public/image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
socketio = SocketIO(app, debug=True, cors_allowed_origins="https://csscrusaders.com")

connections = {}
t_time = {}


# * ----------------------------- TIME OUT SUCKER ----------------------------------

def getIP() -> str:
    return request.headers.get("X-Forwarded-For")


limiter = Limiter(
    key_func=getIP,
    app=app,
    meta_limits=["1 per 30 seconds"],
    application_limits=["50/10 seconds"]
)


# * -------------------------- GET REQUESTS ------------------------------

@app.route("/", methods=["GET"])
@app.route("/public/index.html", methods=["GET"])
def home():
    if "authToken" not in request.cookies:
        return redirect("/authenticate", code=302)
    else:
        token = request.cookies["authToken"].encode()
        h = hashlib.new('sha256')
        h.update(token)
        hashToken = h.hexdigest()

        find_user = user_login.find_one({"authHash": hashToken})
        if not find_user:
            return redirect("/authenticate", code=302)

        username = find_user.get("username")

        return Response(render_template("/index.html", user=username), status="200",
                        headers=[("X-Content-Type-Options", "nosniff")])


@app.route("/get-messages", methods=["GET"])
def get_messages():
    post_handler = PostHandler()
    messages = post_handler.get_all_posts()
    for message in messages:
        message["_id"] = str(message["_id"])
        message['likeCount'] = len(message['likes'])
    return jsonify(messages)


@app.route("/public/favicon.ico", methods=["GET"])
def icon():
    with open("/public/favicon.ico", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "image/x-icon"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/app.js", methods=["GET"])
def javascriptCode():
    with open("/public/app.js", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "text/javascript"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/authenticate.html", methods=["GET"])
def authenticateHTML():
    with open("/public/authenticate.html", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/authenticate", methods=["GET"])
def authenticate():
    readBytes = render_template("/authenticate.html", error="")
    return make_response((readBytes,
                          [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/styles.css", methods=["GET"])
def styles():
    with open("/public/styles.css", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, [("Content-Type", "text/css"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/image/<path:imagePath>", methods=["GET"])
def retrieve_image(imagePath):  # * retrieve images
    return send_from_directory(UPLOAD_FOLDER, imagePath)

@app.route("/profile/<path:username>", methods=["GET"])
def profile(username):
    #if username in the path is equal to connections[request.sid]

    user = User()
    #send them to the editable page

    token = request.cookies.get("authToken")
    val = user.checkLoggedIn(token)
    #h = hashlib.new('sha256')
    #h.update(token)
    #hashToken = h.hexdigest()

    find_user = user_login.find_one({"username":username})

    if find_user:
        if token:
            
            if val != None:
                profile_pic = val["image"]
                bio = val["bio"]
                #now it finds the user
                if username == val["username"]:
                    #set the bio

                    return Response(render_template("/profile.html", user=username, username=username, profile_pic=profile_pic, bio=bio), status="200",
                                headers=[("X-Content-Type-Options", "nosniff")])
                else:

                    return Response(render_template("/otherprofile.html", user=val["username"], username=username, profile_pic=profile_pic, bio=bio), status="200",
                                headers=[("X-Content-Type-Options", "nosniff")])

        else:
            return redirect("/authenticate", code=302)
        
    else:
        return make_response((b"Can't find user", "HTTP/1.1 404 Not Found",
                          [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")]))


@app.errorhandler(404)
def page_not_found(error):
    return make_response((b"Can't find page", "HTTP/1.1 404 Not Found",
                          [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")]))


# * -------------------------------- POST REQUESTS ----------------------------------------

@app.route("/register", methods=["POST"])
def handleSignUp():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        passwordCheck = request.form.get('passwordCheck')

        # TODO: placeholder code

        if password != passwordCheck:
            return Response(render_template("/authenticate.html", error="Passwords are not the same").encode(),
                            status=200, headers=[("X-Content-Type-Options", "nosniff")])
        elif not password and not passwordCheck:
            return Response(
                render_template("/authenticate.html", error="Password and repeated password missing").encode(),
                status=200, headers=[("X-Content-Type-Options", "nosniff")])
        elif not password:
            return Response(render_template("/authenticate.html", error="Password missing").encode(), status=200,
                            headers=[("X-Content-Type-Options", "nosniff")])
        elif not passwordCheck:
            return Response(render_template("/authenticate.html", error="Repeated password missing").encode(),
                            status=200, headers=[("X-Content-Type-Options", "nosniff")])
        else:
            user = User()
            user = user.signup(username, password)

            if user == "Error":
                return Response(b"Error during registration", 400,
                                [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
                # response = make_response((redirect("/", code=302), [("X-Content-Type-Options", "nosniff")]))
            else:
                user_login.update_one({"username": username}, {"$set": {"image": "public/image/image0.png"}})
                user_login.update_one({"username": username}, {"$set": {"bio": "No Bio"}})
                #sets the bio to an empty value on register
                if image_id_collection.find_one({}) is None:
                    image_id_collection.insert_one({"id": 0})
                return Response(b"User Registered", "200 OK",
                                [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/login", methods=["POST"])
def handleLogin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # TODO: placeholder code
        authToken = User()
        authToken = authToken.login(username, password)
        if authToken == "Invalid username/password":
            # * error occurred
            return Response(b"Invalid username/password", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        else:

            response = Response(b"", status=302, headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/")])
            response.set_cookie('authToken', authToken, max_age=3600,
                                httponly=True)  # TODO: change "placeholder" to auth token to give user the cookies.

            return response  # * redirect back to homepage
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/logout", methods=["POST"])
def handleLogout():
    if request.method == "POST":
        authToken = request.cookies.get("authToken")
        if authToken:
            user = User()
            user.logout(authToken)
            response = Response(b"", status=302,
                                headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/authenticate")])
            return response
        else:
            return Response(b"Cookie Not Found", 405,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/file-upload", methods=["POST"])
def indexPicUpload():
    if request.method == "POST":
        if 'file' not in request.files:
            return Response(b"No file", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        # * allowedExtensions = {'.jpg', '.jpeg', '.jfif', 'pjpeg', 'pjp', 'png', }
        file = request.files['file']
        if file.filename == '':
            return Response(b"No selected file", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        fileInfo = fleep.get(file.stream.read())
        if file and fileInfo.type_matches('raster-image'):
            user = User()
            if "authToken" not in request.cookies:
                return redirect("/authenticate", code=302)
            userDoc = user.checkLoggedIn(request.cookies["authToken"])
            if userDoc:
                file.seek(0)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                       f"image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"))
                user_login.update_one({"username": userDoc["username"]}, {"$set": {
                    "image": f"/public/image/image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"}})
                image_id_collection.insert_one({"id": image_id_collection.count_documents({})})
                return redirect("/", 302, Response(b"Redirect", 302, [("Content-Type", "text/plain"),
                                                                      ("X-Content-Type-Options", "nosniff")]))
            else:
                return redirect("/authenticate", code=302)
        else:
            return Response(b"Not image", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    
@app.route("/profile-upload", methods=["POST"])
def profilePicUpload():
    if request.method == "POST":
        if 'file' not in request.files:
            return Response(b"No file", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        # * allowedExtensions = {'.jpg', '.jpeg', '.jfif', 'pjpeg', 'pjp', 'png', }
        file = request.files['file']
        if file.filename == '':
            return Response(b"No selected file", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        fileInfo = fleep.get(file.stream.read())
        if file and fileInfo.type_matches('raster-image'):
            user = User()
            if "authToken" not in request.cookies:
                return redirect("/authenticate", code=302)
            userDoc = user.checkLoggedIn(request.cookies["authToken"])
            if userDoc:
                file.seek(0)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                       f"image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"))
                user_login.update_one({"username": userDoc["username"]}, {"$set": {
                    "image": f"/public/image/image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"}})
                image_id_collection.insert_one({"id": image_id_collection.count_documents({})})
                formatted_string = "/profile/" + userDoc["username"]
                return redirect(str(formatted_string), 302, Response(b"Redirect", 302, [("Content-Type", "text/plain"),
                                                                      ("X-Content-Type-Options", "nosniff")]))
            else:
                return redirect("/authenticate", code=302)
        else:
            return Response(b"Not image", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])



@app.route("/like", methods=["POST"])
def like_post():
    data = request.json
    postId = int(data.get('postId'))
    token = request.cookies["authToken"].encode()
    h = hashlib.new('sha256')
    h.update(token)
    hashToken = h.hexdigest()
    username = user_login.find_one({"authHash": hashToken})
    username = username['username']
    print(username)
    print(postId)
    post_handler = PostHandler()
    post = post_handler.collection.find_one({"post_id": postId})
    print(post)
    if username in post["likes"]:
        post_handler.unlike_post(postId, username)
        liked = False
    else:
        post_handler.like_post(postId, username)
        liked = True
    updated_like_count = post_handler.get_likes(postId)
    response_data = {
        "liked": liked,
        "likeCount": updated_like_count
    }
    return jsonify(response_data)

@app.route("/save-bio", methods=["POST"])
def saveBio():
    if request.method == "POST":
        token = request.cookies.get("authToken")
        if token:
            user = User()
            user = user.checkLoggedIn(token)

            if user:
                user_login.update_one({"username": user["username"]}, {"$set": {"bio": request.files.get("bio")}})
                formatted_string = f"/profile/" + user["username"]
                return redirect(str(formatted_string), 302, Response(b"Redirect", 302, [("Content-Type", "text/plain"),
                                                                      ("X-Content-Type-Options", "nosniff")]))
            else:
                return redirect("/authenticate", code=302)
        else:
            return redirect("/authenticate", code=302)

# * ----------------------------- WEBSOCKETS ----------------------------------------------------------------

# * no need for connection list; socketio handles it

@socketio.on('connect')
def connect():
    user = User()
    user = user.checkLoggedIn(request.cookies.get("authToken"))
    if user:
        global connections
        connections[request.sid] = user["username"]
        username = user["username"]
        print(f"{username} connected")
    else:
        return redirect("/authenticate", code=302)


@socketio.on('disconnect')
def disconnect():
    # emit('disconnect', broadcast=True)
    global connections
    print(f"{connections[request.sid]} disconnected")
    del connections[request.sid]


@socketio.on('message')
def send_mess(mess):
    print(mess)
    username = connections[request.sid]
    curr_user = user_login.find_one({"username": username})
    newPost = PostHandler()
    post = mess.get("message")
    delay = mess.get("delay", 0)
    if post != None and post != "":
        newPost.create_post(str(username), str(post), str(curr_user["image"]))
        message = posts_collection.find_one(sort=[('_id', -1)])  # * very cursed
        message["_id"] = str(message["_id"])
        print(message)

        sentMessage = {'post_id': message["post_id"], 'username': message["username"], 'content': message["content"],
                       'likes': message['likes'], 'likeCount': len(message['likes']), 'image': message['image']}
        if delay > 0:
            update_counter(sentMessage, delay)
        socketio.emit("message", sentMessage)


@socketio.on('like')
def like_post_websockets(postDict):
    postId = postDict.get("postId")
    post_handler = PostHandler()
    post = post_handler.collection.find_one({"post_id": postId})
    username = connections[request.sid]

    if username in post["likes"]:
        post_handler.unlike_post(postId, username)
        liked = False
    else:
        post_handler.like_post(postId, username)
        liked = True
    updated_like_count = post_handler.get_likes(postId)
    socketio.emit("like", {'liked': liked, 'likeCount': updated_like_count, 'postId': postId})


def update_counter(message, delay):
    while delay > 0:
        socketio.emit('counter', {'message': message, 'counter': delay})
        delay = delay - 1
        time.sleep(1)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
    # app.run(host="0.0.0.0", port=8080)
