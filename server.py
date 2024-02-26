from flask import Flask, request, make_response, render_template

app = Flask(__name__)

@app.route("/", methods=["GET"]) 
@app.route("/public/index.html", methods=["GET"])
def home():
    with open("/public/index.html", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK", [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")])

@app.route("/public/styles.css")
def styles():
    with open("/public/styles.css", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK", [("Content-Type", "text/css"), ("X-Content-Type-Options", "nosniff")])

@app.route("/public/image/readme.jpg")
def retrieve_image(): #* retrieve images
    with open("/public/image/readme.jpg", "rb") as file:
        readBytes = file.read()
    return make_response(readBytes, "HTTP/1.1 200 OK", [("Content-Type", "image/jpg"), ("X-Content-Type-Options", "nosniff")])

@app.errorhandler(404)
def page_not_found(error):
    return make_response(b"Can't find page", "HTTP/1.1 404 Not Found", [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    

    