from flask import Flask, make_response, render_template, request, session
from base64 import b64decode
from files.tree import Tree
import subprocess
import sqlite3
import os.path

app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'

conn = sqlite3.connect('trees.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trees (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT, newick TEXT, datetime TEXT)''')
conn.commit()
conn.close()

# TODO move this to the configs!
enable_distances = False
# TODO

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
        # TODO here already without distances too? Maybe, needs to be checked^^
        tree = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode(), enable_distances=enable_distances).to_json()
    elif request.method == "GET":  # TODO post too?
        c.execute('SELECT json FROM trees WHERE id = ?', [session["tree"]])
        tree_json = c.fetchone()[0]
        if enable_distances:
            app_location = __file__[:-6] + "iqtree/iqtree-1.6.12-Linux/"
            result = subprocess.run(
                [os.path.join(app_location, "bin/iqtree"), "-s", app_location + "example.phy", "-te",
                 "(LngfishAu,(LngfishSA,LngfishAf),(Frog,((((Turtle,Crocodile),Sphenodon),Lizard),(((Human,(Seal,(Cow,Whale))),(Bird,(Mouse,Rat))),(Platypus,Opossum)))));", "-nt", "4", "-redo", "-pre", "REMODEL"],
                cwd=app_location)  # , capture_output=True) # TODO CHANGE CWD
            # Model auswählen nach vorherigem?
            # "-m", "TIM2+F+I+G4" / Weglassen
            # Kerne festsetzen wie vorheriges?
            # "-nt", "4" / "-nt", "AUTO"
            print(result)
        tree = Tree(tree_json, request.args.get("from"), request.args.get("to"), enable_distances).to_json()
    else:
        pass  # TODO
    c.execute('INSERT INTO trees (json, datetime) VALUES (?, datetime("now", "localtime"))', [tree])
    session["tree"] = c.lastrowid
    if session.get("trees"):
        session["trees"].append(session["tree"])
    else:
        session["trees"] = [session["tree"]]
    print(session["trees"])
    trees = c.execute('SELECT * FROM trees WHERE id IN ({seq})'.format(seq=','.join(['?']*len(session["trees"]))), session["trees"]).fetchall()
    conn.commit()
    conn.close()
    response = make_response({"tree": tree, "trees": trees})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    #app.run(host='0.0.0.0', port=80)
    app.run()
