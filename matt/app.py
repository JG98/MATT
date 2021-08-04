# MATT - A Framework For Modifying And Testing Topologies
# Copyright (C) 2020 Jeff Raffael Gower
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from flask import Flask, make_response, render_template, request, session, send_from_directory
from base64 import b64decode
from matt.tree import Tree
from json import dumps
import subprocess
import sqlite3
import os.path
import platform
import configparser
import webbrowser
import threading
import time

# TODO constants like app_location to APP_LOCATION
app = Flask(__name__, static_url_path="/static")
app.secret_key = b'H.\xf8\xd7|J\x98\x16/(\x86\x05X\xf8")\x11\x9dM\x08\xcc\xfe\xa2\x03'
root_folder = __file__[:-6]
system = platform.system()
if platform.system() == "Darwin":
    system = "MacOSX"
app_location = os.path.join(root_folder, "iqtree", "iqtree-1.6.12-" + system, "")
if platform.system() == "Windows":
    addition = ".exe"
else:
    addition = ""
os.chmod(os.path.join(app_location, "bin", "iqtree" + addition), 0o755)
config = configparser.ConfigParser()
config_path = os.path.join(root_folder, "config.ini")


@app.route("/")
def home():
    session["trees"] = []
    # TODO set options from file
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/get-options", methods=["GET"])
def get_options():
    config.read(config_path)
    while not config.has_section("Options"):
        set_default_config()
    else:
        enable_lengths = config.getboolean("Options", "enable-lengths")
        dna_protein = config.get("Options", "dna-protein")
        dna_bsr = config.get("Options", "dna-bsr")
        dna_bf = config.get("Options", "dna-bf")
        dna_rhas = config.get("Options", "dna-rhas")
        protein_aaerm = config.get("Options", "protein-aaerm")
        protein_pmm = config.get("Options", "protein-pmm")
        protein_aaf = config.get("Options", "protein-aaf")
        protein_rhas = config.get("Options", "protein-rhas")
    options = dumps({"enable_lengths": enable_lengths,
                     "dna_protein": dna_protein,
                     "dna_bsr": dna_bsr,
                     "dna_bf": dna_bf,
                     "dna_rhas": dna_rhas,
                     "protein_aaerm": protein_aaerm,
                     "protein_pmm": protein_pmm,
                     "protein_aaf": protein_aaf,
                     "protein_rhas": protein_rhas})
    response = make_response(options)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/download/<tree_id>", methods=["GET"])
def download(tree_id):
    path = os.path.join(root_folder, "tmp", "download.nck")
    file = open(path, "w")
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    tree_db = c.execute("SELECT json, description FROM trees WHERE id = ?", (tree_id,)).fetchall()
    tree_json = tree_db[0][0]
    tree_description = tree_db[0][1]
    tree = Tree(tree_json).to_newick()
    file.write(tree + "\n")
    file.close()
    return send_from_directory(os.path.join(root_folder, "tmp"), "download.nck", as_attachment=True,
                               attachment_filename=tree_description + ".nck")


@app.route("/description", methods=["POST"])
def description():
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    form_id = request.form.get("id")
    form_description = request.form.get("description")
    rowcount = c.execute("UPDATE trees SET description = ? WHERE id = ?", (form_description, form_id)).rowcount
    conn.commit()
    if rowcount == 1:
        response = make_response("OK")
        response.headers["Cache-Control"] = "no-store"
        return response
    else:
        response = make_response("FAILED")
        response.headers["Cache-Control"] = "no-store"
        return response


@app.route("/load", methods=["POST", "GET"])
def load():
    model = None
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    # TODO
    config.read(config_path)
    while not config.has_section("Options"):
        set_default_config()
    else:
        enable_lengths = config.getboolean("Options", "enable-lengths")
        dna_protein = config.get("Options", "dna-protein")
        if dna_protein == "dna":
            dna_bsr = config.get("Options", "dna-bsr")
            dna_bf = config.get("Options", "dna-bf")
            dna_rhas = config.get("Options", "dna-rhas")
            model = dna_bsr
            if dna_bf != "-":
                model += "+" + dna_bf
            if dna_rhas != "-":
                model += "+" + dna_rhas
        elif dna_protein == "protein":
            protein_aaerm = config.get("Options", "protein-aaerm")
            protein_pmm = config.get("Options", "protein-pmm")
            protein_aaf = config.get("Options", "protein-aaf")
            protein_rhas = config.get("Options", "protein-rhas")
            model = protein_aaerm
            if protein_pmm != "-":
                model += "+" + protein_pmm
            if protein_aaf != "-":
                model += "+" + protein_aaf
            if protein_rhas != "-":
                model += "+" + protein_rhas
    # TODO not POST/GET rather one or two form args or none if it is just a reload from saving options (TODO)
    disable_testing = False

    if request.method == "POST":
        # TODO always delete tmp afterwards maybe??
        # TODO here already without lengths too? Maybe, needs to be checked^^
        alignment = tree = None

        if request.form.get("example") is not None:
            example_alignment = open(os.path.join(root_folder, "static", "example.phy"), "r")
            alignment = example_alignment.read()
            example_alignment.close()

            example_tree = open(os.path.join(root_folder, "static", "example.treefile"), "r")
            tree = example_tree.read()
            example_tree.close()
        else:
            if request.form.get("alignment[data]") is not None:
                alignment = b64decode(request.form.get("alignment[data]").split("base64,")[1]).decode()
                # alignment_type = request.form.get("alignment[name]").split(".")[-1]
            if request.form.get("tree[data]") is not None:
                tree = b64decode(request.form.get("tree[data]").split("base64,")[1]).decode()
                # tree_type = request.form.get("tree[name]").split(".")[-1]

        if alignment is not None and tree is not None:  # Case 1, alignment and tree given, default behaviour
            with open(os.path.join(root_folder, "tmp", "alignment.phy"), "w") as alignment_file:
                alignment_file.write(alignment)
            tree = Tree(tree, enable_lengths=enable_lengths).to_json()
        elif alignment is not None:  # Case 2, only alignment given, construct ml-tree
            with open(os.path.join(root_folder, "tmp", "alignment.phy"), "w") as alignment_file:
                alignment_file.write(alignment)
            if model is not None:
                print("Starting IQTree. This could take some time!")
                sp = subprocess.run([os.path.join(app_location, "bin", "iqtree"), "-s",
                                     os.path.join(root_folder, "tmp", "alignment.phy"), "-m", model, "-redo"],
                                    capture_output=True)
                print(sp)
                if sp.returncode == 2:
                    print("WRONG DECISION DNA/PROTEIN")
            else:
                print("Starting IQTree. This could take some time!")
                sp = subprocess.run([os.path.join(app_location, "bin", "iqtree"), "-s",
                                     os.path.join(root_folder, "tmp", "alignment.phy"), "-redo"], capture_output=True)
                print(sp)
            with open(os.path.join(root_folder, "tmp", "alignment.phy.treefile"), "r") as tree_file:
                tree = tree_file.readline()
            tree = Tree(tree[:-1], enable_lengths=enable_lengths).to_json()
        elif tree is not None:  # Case 3, only tree given, disable testing and lengths
            enable_lengths = False
            tree = Tree(tree, enable_lengths=enable_lengths).to_json()
            disable_testing = True
    elif request.method == "GET":  # TODO post too?
        c.execute('SELECT json FROM trees WHERE id = ?', [session["tree"]])
        tree_json = c.fetchone()[0]
        print(request.args)
        if len(request.args) == 0:
            json_args = None
        if request.args.get("id") is not None:
            json_args = [request.args.get("id")]
        elif request.args.get("from") is not None:
            json_args = [request.args.get("from"), request.args.get("to")]
        else:
            pass  # TODO
        if request.args.get("current") is not None:
            current = request.args.get("current")
        else:
            current = None
        if enable_lengths:
            # TODO same for case 2, provide options there too
            tree = Tree(tree_json, json_args, enable_lengths).to_newick(True)
            path = os.path.join(root_folder, "tmp", "tree.nck")
            file = open(path, "w")
            file.write(tree + "\n")
            file.close()
            print("Starting IQTree. This could take some time!")
            sp = subprocess.run([os.path.join(app_location, "bin", "iqtree"), "-s", os.path.join(root_folder, "tmp",
                                                                                                 "alignment.phy"),
                                 "-te", path, "-nt", "4", "-m", model, "-redo"], capture_output=True)
            print(sp)
            if sp.returncode == 2:
                print("WRONG DECISION DNA/PROTEIN")
            with open(os.path.join(root_folder, "tmp", "alignment.phy.treefile"), "r") as tree_file:
                tree = tree_file.readline()
            tree = Tree(tree[:-1], enable_lengths=enable_lengths).to_json()
        else:
            tree = Tree(tree_json, json_args, enable_lengths).to_json()
        if current is not None:
            del session["trees"][int(current):]
    else:
        pass  # TODO

    c.execute('INSERT INTO trees (json, datetime) VALUES (?, datetime("now", "localtime"))', [tree])
    session["tree"] = c.lastrowid
    session["trees"].append(session["tree"])
    print(session["trees"])
    trees = c.execute('SELECT * FROM trees WHERE id IN ({seq})'.format(seq=','.join(['?'] * len(session["trees"]))),
                      session["trees"]).fetchall()
    conn.commit()
    conn.close()
    response = make_response(dumps(trees))
    response.headers["Cache-Control"] = "no-store"
    if disable_testing:
        response.headers["Testing"] = "disabled"
    else:
        response.headers["Testing"] = "enabled"
    return response


@app.route("/reset/<tree_id>", methods=["GET"])
def reset(tree_id):
    session["trees"] = [tree_id]
    response = make_response("OK")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/options", methods=["POST"])
def options():
    config.read(config_path)
    while not config.has_section("Options"):
        set_default_config()
    else:
        config.set("Options", "enable-lengths", request.form.get("enable-lengths"))

    if request.form.get("dna-protein") == "dna" or request.form.get("dna-protein") == "protein":
        config.set("Options", "dna-protein", request.form.get("dna-protein"))

    if request.form.get("dna-protein") == "dna":
        config.set("Options", "dna-bsr", request.form.get("dna-bsr"))
        config.set("Options", "dna-bf", request.form.get("dna-bf"))
        config.set("Options", "dna-rhas", request.form.get("dna-rhas"))
    elif request.form.get("dna-protein") == "protein":
        config.set("Options", "protein-aaerm", request.form.get("protein-aaerm"))
        config.set("Options", "protein-pmm", request.form.get("protein-pmm"))
        config.set("Options", "protein-aaf", request.form.get("protein-aaf"))
        config.set("Options", "protein-rhas", request.form.get("protein-rhas"))
    with open(root_folder + "config.ini", "w") as config_file:
        config.write(config_file)
    response = make_response("OK")  # TODO
    # TODO PRINT NEW TREE (options to the whole data thingy too)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/tests", methods=["POST"])
def tests():
    # TODO handle that testing is disabled but ppl still try to test
    snapshots = request.form.getlist("snapshots[]")
    path = os.path.join(root_folder, "tmp", "tests.nck")
    file = open(path, "w")
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    trees_json = c.execute("SELECT json FROM trees WHERE id IN ({})".format(','.join('?' for _ in snapshots)),
                           snapshots).fetchall()
    # TODO USE REAL LENGTHS NO MATTER WHAT ENABLE_LENGTHS IS!
    for tree_json in trees_json[:-1]:
        tree = Tree(tree_json[0]).to_newick()
        file.write(tree)
    file.write(Tree(trees_json[-1][0]).to_newick())
    file.close()

    config.read(config_path)
    while not config.has_section("Options"):
        set_default_config()
    else:
        dna_protein = config.get("Options", "dna-protein")
        if dna_protein == "dna":
            dna_bsr = config.get("Options", "dna-bsr")
            dna_bf = config.get("Options", "dna-bf")
            dna_rhas = config.get("Options", "dna-rhas")
            model = dna_bsr
            if dna_bf != "-":
                model += "+" + dna_bf
            if dna_rhas != "-":
                model += "+" + dna_rhas
        elif dna_protein == "protein":
            protein_aaerm = config.get("Options", "protein-aaerm")
            protein_pmm = config.get("Options", "protein-pmm")
            protein_aaf = config.get("Options", "protein-aaf")
            protein_rhas = config.get("Options", "protein-rhas")
            model = protein_aaerm
            if protein_pmm != "-":
                model += "+" + protein_pmm
            if protein_aaf != "-":
                model += "+" + protein_aaf
            if protein_rhas != "-":
                model += "+" + protein_rhas
    print("Starting IQTree. This could take some time!")
    sp = subprocess.run(
        [os.path.join(app_location, "bin", "iqtree"), "-s", os.path.join(root_folder, "tmp", "alignment.phy"), "-z",
         path, "-n", "0", "-zb", "10000", "-zw", "-au", "-m", model, "-redo"]) # TODO capture_output=True
    print(sp)
    results = []
    path = os.path.join(root_folder, "tmp", "alignment.phy.iqtree")
    file = open(path, "r")
    for line in file:
        if line.startswith(
                "-------------------------------------------------------------------------------------------"):
            for j in range(len(snapshots)):
                results.append(next(file).strip().split())
    file.close()
    response = make_response(dumps(results))
    response.headers["Cache-Control"] = "no-store"
    return response


def set_default_config():
    config["Options"] = {
        'enable-lengths': 'false',
        'dna-protein': 'dna',
        'dna-bsr': 'JC',
        'dna-bf': '-',
        'dna-rhas': '-',
        'protein-aaerm': 'Blosum62',
        'protein-pmm': '-',
        'protein-aaf': '-',
        'protein-rhas': '-'
    }
    with open(root_folder + "config.ini", "w") as config_file:
        config.write(config_file)


def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000/")


def main():
    conn = sqlite3.connect(root_folder + 'trees.db')
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS trees''')
    c.execute(
        '''CREATE TABLE trees (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT, description TEXT, datetime TEXT)''')
    conn.commit()
    conn.close()

    if not os.path.exists(root_folder + "config.ini"):
        set_default_config()

    if not os.path.exists(os.path.join(root_folder, "tmp")):
        os.makedirs(os.path.join(root_folder, "tmp"))

    thread = threading.Thread(target=open_browser)
    thread.start()

    # app.run(host='127.0.0.1', port=80)
    # app.run(host='0.0.0.0', port=80)
    app.run()


if __name__ == '__main__':
    main()
