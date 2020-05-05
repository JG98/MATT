from flask import Flask, make_response, render_template, request, session
from base64 import b64decode
from files.tree import Tree
from json import dumps
import subprocess
import sqlite3
import os.path
import platform

app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'
root_folder = __file__[:-6]
system = platform.system()
if platform.system() == "Darwin":
    system = "MacOSX"
app_location = root_folder + "iqtree\iqtree-1.6.12-" + system + "\\"

conn = sqlite3.connect(root_folder + 'trees.db')
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS trees''')
c.execute('''CREATE TABLE trees (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT, datetime TEXT)''')
conn.commit()
conn.close()


@app.route("/")
def home():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/load", methods=["POST", "GET"])
def load():
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    # TODO
    if session["options"]:
        enable_distances = session["options"].get("enable-distances", False)
    else:
        enable_distances = False
        # TODO SET session["options"]
    print(enable_distances)
    # TODO not POST/GET rather one or two form args or none if it is just a reload from saving options (TODO)
    print(len(request.args))
    print(len(request.form))
    if request.method == "POST":
        # TODO here already without distances too? Maybe, needs to be checked^^
        tree = Tree(b64decode(request.form.get("file").split("base64,")[1]).decode(), enable_distances=enable_distances).to_json()
    elif request.method == "GET":  # TODO post too?
        c.execute('SELECT json FROM trees WHERE id = ?', [session["tree"]])
        tree_json = c.fetchone()[0]
        if enable_distances:
            result = subprocess.run(
                [os.path.join(app_location, "bin/iqtree"), "-s", app_location + "example.phy", "-te",
                 "(LngfishAu,(LngfishSA,LngfishAf),(Frog,((((Turtle,Crocodile),Sphenodon),Lizard),(((Human,(Seal,(Cow,Whale))),(Bird,(Mouse,Rat))),(Platypus,Opossum)))));", "-nt", "4", "-redo", "-pre", "REMODEL"])
            # Model auswählen nach vorherigem?
            # "-m", "TIM2+F+I+G4" / Weglassen
            # Kerne festsetzen wie vorheriges?
            # "-nt", "4" / "-nt", "AUTO"

            # ERST RICHTIGES MODEL FINDEN
            print(result)
            # TODO use result??
        if len(request.args) == 1:
            json_args = [request.args.get("id")]
        elif len(request.args) == 2:
            json_args = [request.args.get("from"), request.args.get("to")]
        else:
            pass  #TODO
        print(json_args)
        tree = Tree(tree_json, json_args, enable_distances).to_json()
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


@app.route("/options", methods=["POST"])
def options():
    session["options"] = {"enable-distances": request.form.get("enable-distances") == "true"}
    response = make_response(session["options"])
    print(session["options"])
    # TODO PRINT NEW TREE (options to the whole data thingy too)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/tests", methods=["POST"])
def tests():
    snapshots = request.form.getlist("snapshots[]")
    path = os.path.join(root_folder, "tmp/trees.txt")
    file = open(path, "w")
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    trees_json = c.execute(f"SELECT json FROM trees WHERE id IN ({','.join('?' for _ in snapshots)})", snapshots).fetchall()
    # TODO USE REAL DISTANCES THO!
    for tree_json in trees_json[:-1]:
        tree = Tree(tree_json[0]).to_newick()
        file.write(tree + "\n")
    file.write(Tree(trees_json[-1][0]).to_newick())
    file.close()
    subprocess.run([os.path.join(app_location, "bin/iqtree"), "-s", app_location + "example.phy", "-z", path, "-n", "0",
                    "-zb", "10000", "-zw", "-au", "-redo"])
    results = []
    path = app_location + "example.phy.iqtree"
    file = open(path, "r")
    for line in file:
        if line.startswith("-------------------------------------------------------------------------------------------"):
            for j in range(len(snapshots)):
                results.append(next(file).strip().split())
    print(results)
    print(dumps(results))
    response = make_response(dumps(results))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Topology tests
# iqtree -s ../example.phy -z ../TEST.treels -n 0 -zb 1000 -zw -au


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    #app.run(host='0.0.0.0', port=80)
    app.run()
