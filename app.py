from flask import Flask, make_response, render_template, request
from base64 import b64decode
from files.tree import Tree

app = Flask(__name__, static_url_path="/static")


@app.route("/")
def home():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/load", methods=["POST"])
def load():
    tree = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode())
    response = make_response(tree.to_json())
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    app.run(host='0.0.0.0', port=80)
