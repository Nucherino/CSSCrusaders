from flask import Flask, request, make_response, redirect, render_template, Response
from database import user_login
from userClass import User
import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

app = Flask(__name__, template_folder='public')

# * -------------------------- GET REQUESTS ------------------------------

@app.route("/", methods=["GET"])
@app.route("/public/index.html", methods=["GET"])
def home():
    user = User()
    if "authtoken" not in request.cookies:
        return make_response(redirect("/login", code = 401))
    else:
        token = request.cookies["authtoken"]
        find_user = user.find({"authtoken": token})
        if find_user == None:
            return make_response(redirect("/login", code=401))
    with open("/public/index.html", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, 
                         [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))

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


@app.route("/signup")
def signup():
    readBytes = render_template("signup.html", error="")
    return make_response((readBytes, 
                         [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/styles.css")
def styles():
    with open("/public/styles.css", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, [("Content-Type", "text/css"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/image/readme.jpg")
def retrieve_image():  # * retrieve images
    with open("/public/image/readme.jpg", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, [("Content-Type", "image/jpg"), ("X-Content-Type-Options", "nosniff")]))


@app.errorhandler(404)
def page_not_found(error):
    return make_response((b"Can't find page", "HTTP/1.1 404 Not Found", 
                         [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")]))


# * -------------------------------- POST REQUESTS ----------------------------------------

@app.route("/register", methods=["POST"])
def handleSignUp():
    username = request.form.get('username')
    password = request.form.get('password')
    passwordCheck = request.form.get('passwordCheck')

    # TODO: placeholder code

    if password != passwordCheck:
        return render_template("signup.html", error="Passwords are not the same")
    elif not password and not passwordCheck:
        return render_template("signup.html", error="Password and repeated password missing")
    elif not password:
        return render_template("signup.html", error="Password missing")
    elif not passwordCheck:
        return render_template("signup.html", error="Repeated password missing")
    else:
        user = user.signup(user, username, password)

        if user.get("Success"):
            return Response(b"User Registered", "200 OK", [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        #response = make_response((redirect("/", code=302), [("X-Content-Type-Options", "nosniff")]))
        else:
            return Response(b"Error during registration", 400, [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])

@app.route("/login", methods=["POST"])
def handleLogin():
    username = request.form.get('username')
    password = request.form.get('password')

    
    # TODO: placeholder code
    authToken = User.login(authToken, username, password)
    if type(authToken) == type(Response):
        #* error occurred
        return Response(b"Invalid username/password", 400, [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        
        response = make_response((redirect("/", code=302), [("X-Content-Type-Options", "nosniff")]))
        response.set_cookie('authToken', authToken, max_age=3600,
                            httponly=True)  # TODO: change "placeholder" to auth token to give user the cookies.
        return response  # * redirect back to homepage

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
