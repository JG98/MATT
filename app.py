from flask import Flask, make_response, render_template, request, session
from base64 import b64decode
from files.tree import Tree
import sqlite3

app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'

@app.route("/")
def home():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/load", methods=["POST", "GET"])
def load():
    conn = sqlite3.connect('trees.db')
    c = conn.cursor()
    if request.method == "POST":
        tree = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode()).to_json()
        c.execute('''INSERT INTO trees (json) VALUES (?)''', [tree])
        session["tree"] = c.lastrowid
    elif request.method == "GET":
        c.execute('''SELECT json FROM trees WHERE id = ?''', [session["tree"]])
        tree = Tree(c.fetchone()[0], request.args.get("from"), request.args.get("to")).to_json()
    else:
        pass # TODO
    conn.commit()
    conn.close()
    response = make_response(tree)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    #app.run(host='0.0.0.0', port=80)
    app.run()

    conn = sqlite3.connect('trees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trees (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT)''')
    conn.commit()
    conn.close()
