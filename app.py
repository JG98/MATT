from flask import Flask, make_response, render_template, request, session
from base64 import b64decode
from files.tree import Tree
from json import dumps
import subprocess
import sqlite3
import os.path
import platform
import configparser

# TODO constants like app_location to APP_LOCATION

app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'
root_folder = __file__[:-6]
system = platform.system()
if platform.system() == "Darwin":
    system = "MacOSX"
app_location = os.path.join(root_folder, "iqtree", "iqtree-1.6.12-" + system, "")

conn = sqlite3.connect(root_folder + 'trees.db')
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS trees''')
c.execute('''CREATE TABLE trees (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT, datetime TEXT)''')
conn.commit()
conn.close()


@app.route("/")
def home():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/load", methods=["POST", "GET"])
def load():
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    # TODO
    config.read("config.ini")
    enable_lengths = config.get("Options", "enable-lengths")
    print("def" + str(enable_lengths))
    # TODO not POST/GET rather one or two form args or none if it is just a reload from saving options (TODO)
    print(len(request.args))
    print(len(request.form))
    if request.method == "POST":
        # TODO 1st (default case): Enter alignment and tree and we save both
        # TODO 2nd case: Enter only alignment and hope that tree calculation does not need higher specs that you have
        # TODO 3rd case: Enter only tree and we disable test option, because we have no alignment
        # TODO this here is case 2 currently

        # TODO always delete temp afterwards mabye??
        # TODO here already without lengths too? Maybe, needs to be checked^^
        alignment = b64decode(request.form.get("file[data]").split("base64,")[1]).decode()
        # TODO tree = b64decode(request.form.get("tree-file[data]").split("base64,")[1]).decode()
        alignment_type = request.form.get("file[name]").split(".")[-1]
        # TODO tree_type = request.form.get("alignment-file[name]").split(".")[-1]

        with open(os.path.join("tmp", "alignment." + alignment_type), "w") as alignment_file:
            alignment_file.write(alignment)
        subprocess.run([os.path.join(app_location, "bin/iqtree"), "-s", os.path.join("tmp", "alignment." + alignment_type), "-m", "Blosum62"])
        with open(os.path.join("tmp", "alignment." + alignment_type + ".treefile"), "r") as tree_file:
            tree = tree_file.readline()
        tree = Tree(tree[:-1], enable_lengths=enable_lengths).to_json()
    elif request.method == "GET":  # TODO post too?
        c.execute('SELECT json FROM trees WHERE id = ?', [session["tree"]])
        tree_json = c.fetchone()[0]
        if enable_lengths:
            pass
            #result = subprocess.run(
            #    [os.path.join(app_location, "bin/iqtree"), "-s", app_location + "example.phy", "-te",
            #     "(LngfishAu,(LngfishSA,LngfishAf),(Frog,((((Turtle,Crocodile),Sphenodon),Lizard),(((Human,(Seal,(Cow,Whale))),(Bird,(Mouse,Rat))),(Platypus,Opossum)))));", "-nt", "4", "-redo", "-pre", "REMODEL"])
            # Model auswählen nach vorherigem?
            # "-m", "TIM2+F+I+G4" / Weglassen
            # Kerne festsetzen wie vorheriges?
            # "-nt", "4" / "-nt", "AUTO"

            # ERST RICHTIGES MODEL FINDEN
            #print(result)
            # TODO use result??
        #if len(request.args) == 0:
        #    json_args = None
        if len(request.args) == 1:
            json_args = [request.args.get("id")]
        elif len(request.args) == 2:
            json_args = [request.args.get("from"), request.args.get("to")]
        else:
            pass  #TODO
        print(json_args)
        tree = Tree(tree_json, json_args, enable_lengths).to_json()
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
    response = make_response(dumps(trees))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/options", methods=["POST"])
def options():
    print(request.form)
    print(request.form.get("enable-lengths"))
    config.read("config.ini")
    if not config.has_section("Options"):
        config.add_section("Options")
    config.set("Options", "enable-lengths", request.form.get("enable-lengths"))
    config.set("Options", "dna-protein", request.form.get("dna-protein"))
    if request.form.get("dna-protein") == "dna":
        config.set("Options", "dna-bsr", request.form.get("dna-bsr"))
        config.set("Options", "dna-bf", request.form.get("dna-bf"))
        config.set("Options", "dna-rhas", request.form.get("dna-rhas"))
    elif request.form.get("dna-protein") == "protein":
        config.set("Options", "protein-aaerm", request.form.get("protein-aaerm"))
        config.set("Options", "protein-pmm", request.form.get("protein-pmm"))
        config.set("Options", "protein-aaf", request.form.get("protein-aaf"))
    save_config()
    #response = make_response(dumps(config.getboolean("Options", "enable-lengths")))
    #print("abc" + str(config.getboolean("Options", "enable-lengths")))
    response = make_response("OK")  # TODO
    # TODO PRINT NEW TREE (options to the whole data thingy too)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/tests", methods=["POST"])
def tests():
    snapshots = request.form.getlist("snapshots[]")
    path = os.path.join(root_folder, "tmp", "trees.nck")
    file = open(path, "w")
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    trees_json = c.execute("SELECT json FROM trees WHERE id IN ({})".format(','.join('?' for _ in snapshots)), snapshots).fetchall()
    # TODO USE REAL LENGTHS THO!
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
    response.headers["Cache-Control"] = "no-store"
    return response


def save_config():
    config["DEFAULT"] = {
        'enable-lengths': 'true',
        'dna-protein': 'dna',
        'dna-bsr': 'JC',
        'dna-bf': '-',
        'dna-rhas': '-'
    }
    with open(root_folder + "config.ini", "w") as config_file:
        config.write(config_file)


config = configparser.ConfigParser()
if not os.path.exists(root_folder + "config.ini"):
    save_config()


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=80)
    #app.run(host='0.0.0.0', port=80)
    app.run()

