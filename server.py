import html, fleep, os, json
from flask import Flask, request, make_response, redirect, render_template, send_from_directory, Response, jsonify
from flask_socketio import SocketIO
from database import *
from userClass import *
import mimetypes, hashlib
from postClass import PostHandler

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/jpg', '.jpg')

app = Flask(__name__, template_folder='public')
UPLOAD_FOLDER = '/public/image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

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

        # with open("public/index.html", "r") as html:
        #    body = html.read()
        # soup = BeautifulSoup(body, "html.parser")
        # old_text = soup.find(id = "username-form")
        # new_text = old_text.find(text=re.compile("{{user}}")).replace_with(find_user.get("username"))

        name = find_user.get("username")

        user = name

        posts = PostHandler()

        # old_post = soup.find()
        initial_like_counts = {}
        for post in posts.get_all_posts_sorted_by_id():
            post_id = post["post_id"]
            like_count = posts.get_likes(post_id)
            initial_like_counts[post_id] = like_count

        # body = soup.prettify("utf-8")
        # response = make_response(body, 200)
        # response.headers.set("X-Content-Type-Options", "nosniff")
        # response.headers.set("posts", posts=posts.get_all_posts_sorted_by_id)
        # return response

        return Response(render_template("/index.html", posts=posts.get_all_posts_sorted_by_id(),
                                        initial_like_counts=initial_like_counts, user=user), status="200",
                        headers=[("X-Content-Type-Options", "nosniff")])


#@socketio.on('new_post') This may need to be added for posts later on - but alterations to front end may need to be made
#def handle_new_post(data):
#    send(data, broadcast=True)

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


@app.route("/chat-messages", methods=["POST"])
def posts():
    if "authToken" not in request.cookies:
        return redirect("/authenticate", code=302)
    else:
        token = request.cookies["authToken"].encode()
        h = hashlib.new('sha256')
        h.update(token)
        hashToken = h.hexdigest()

        find_user = user_login.find({"authHash": hashToken})
        if not find_user:
            return redirect("/authenticate", code=302)
        else:
            newPost = PostHandler()
            username = user_login.find_one({"authHash": hashToken})
            post = json.loads(request.get_data()).get("message")
            #post = post["message"]
            if post != None and post != "":
                newPost.create_post(str(username[username["username"]]), str(post), str(username["image"]))
                # this may havwe to be changed to "emit" function from socket io for messages
            return Response(b"", status=302, headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/")])


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

@app.route("/file-upload", methods=["POST"])
def profilePicUpload():
    if request.method == "POST":
        if 'file' not in request.files:
            return Response(b"No file", 400,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        #* allowedExtensions = {'.jpg', '.jpeg', '.jfif', 'pjpeg', 'pjp', 'png', }
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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"))
                user_login.update_one({"username": userDoc["username"]}, {"$set": {"image": f"/public/image/image{image_id_collection.count_documents({})}.{fileInfo.extension[0]}"}})
                image_id_collection.insert_one({"id":image_id_collection.count_documents({})})
                return redirect("/", 302, Response(b"Redirect", 302, [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")]))
            else:
                return redirect("/authenticate", code=302)
        else:
            return Response(b"Not image", 400,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    

