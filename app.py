from flask import Flask, make_response, render_template, request, session
from base64 import b64decode
from files.tree import Tree
from pymongo import MongoClient
from uuid import uuid4

app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'

client = MongoClient()
db = client.database
collection = db.collection

@app.route("/")
def home():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/load", methods=["POST", "GET"])
def load():
    if request.method == "POST":
        uuid = str(uuid4())
        tree = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode()).to_json()
        post_id = collection.insert_one({"id": uuid, "tree": tree})
        # TODO localStorage in JS or flask_session or pymongo
        session["tree"] = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode()).to_json()
        print(session["tree"])
    elif request.method == "GET":
        # TODO localStorage in JS or flask_session or pymongo
        session["tree"] = Tree(session["tree"], request.args.get("from"), request.args.get("to")).to_json()
    else:
        pass # TODO
    # TODO localStorage in JS or flask_session or pymongo
    response = make_response(session["tree"])
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    #app.run(host='0.0.0.0', port=80)
    app.run()
