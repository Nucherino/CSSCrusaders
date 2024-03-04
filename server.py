from flask import Flask, request, make_response, redirect, render_template
from database import user_login
from userClass import User

app = Flask(__name__, template_folder='public')

# * -------------------------- GET REQUESTS ------------------------------

@app.route("/", methods=["GET"])
@app.route("/public/index.html", methods=["GET"])
def home():
    with open("/public/index.html", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK",
                         [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")])


@app.route("/public/app.js", methods=["GET"])
def javascriptCode():
    with open("/public/app.js", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK",
                         [("Content-Type", "text/javascript"), ("X-Content-Type-Options", "nosniff")])


@app.route("/signup")
def signup():
    readBytes = render_template("signup.html", error="")
    return make_response(readBytes, "HTTP/1.1 200 OK",
                         [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")])


@app.route("/public/styles.css")
def styles():
    with open("/public/styles.css", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK",
                         [("Content-Type", "text/css"), ("X-Content-Type-Options", "nosniff")])


@app.route("/public/image/readme.jpg")
def retrieve_image():  # * retrieve images
    with open("/public/image/readme.jpg", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK",
                         [("Content-Type", "image/jpg"), ("X-Content-Type-Options", "nosniff")])


@app.errorhandler(404)
def page_not_found(error):
    return make_response(b"Can't find page", "HTTP/1.1 404 Not Found",
                         [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


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
        user = User()
        User.signup(user, username, password)
        # TODO: create auth token, store hashed auth token in database

        response = make_response(redirect("/", code=302))
        response.set_cookie('authtoken', "placeholder", 3600,
                            httponly=True)  # TODO: change "placeholder" to auth token to give user the cookies.
        return response  # * redirect back to homepage


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
