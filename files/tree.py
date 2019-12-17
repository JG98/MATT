from files.node import Node
from json import dumps, loads
from decimal import Decimal, getcontext

getcontext().prec = 10


class Tree:

    def __init__(self, string, from_id=None, to_id=None):
        if string[-1] == ";":
            self.from_newick(string[1:-2])
            # TODO PREPARE newick, e.g. remove all \n
        else:
            self.from_json(string, from_id, to_id)

    def from_newick(self, newick):
        self.node_counter = 0
        self.root = Node(self.node_counter, Decimal(0), Decimal(0))  # TODO BOOTSTRAP FOR EVEN THE FIRST TWO NODES?
        self.node_counter += 1
        level = 0
        # TODO PREPARE newick, e.g. remove all \n
        last_comma = -1
        last_colon = newick.rfind(":")

        for i, char in enumerate(newick[::-1]):
            if char == "(":
                level += 1
            elif char == ")":
                level -= 1
            elif char == "," and level == 0 and last_comma == -1:
                last_comma = len(newick) - i - 1

        for i, char in enumerate(newick):
            if char == "(":
                level += 1
            elif char == ")":
                level -= 1
            elif char == "," and level == 0:
                if i == last_comma:
                    self.root.l_child = self.make_node_from_newick(newick[:i], self.root)
                    self.root.r_child = self.make_node_from_newick(newick[i + 1:], self.root)
                    return
                else:
                    distance = Decimal(newick[last_colon + 1:]) / 2
                    self.root.l_child = self.make_node_from_newick(
                        "(" + newick[:last_comma] + "):" + str(distance), self.root)
                    self.root.r_child = self.make_node_from_newick(
                        newick[last_comma+1:last_colon] + ":" + str(distance), self.root)
                    return

    def from_json(self, string, from_id, to_id):
        json = loads(string)
        json.pop()
        nodes = {}
        for node in json:
            nodes[int(node["id"])] = Node(node.get("id"), Decimal(node.get("distance")),
                                          Decimal(node.get("total_distance")), node.get("parent"), node.get("l_child"),
                                          node.get("r_child"), node.get("name"), node.get("bootstrap"))
        for node in nodes.values():
            if node.parent != "":
                node.parent = nodes[int(node.parent)]
            if node.l_child != "":
                node.l_child = nodes[int(node.l_child)]
            if node.r_child != "":
                node.r_child = nodes[int(node.r_child)]
        self.root = nodes[0]

        for node in nodes.values():
            print(node.__dict__)

        # REHANG
        # TODO

        for node in nodes.values():
            print(node.__dict__)

    def make_node_from_newick(self, string, parent):
        colon = string.rfind(":")
        last_parenthesis = string.rfind(")")
        distance = Decimal(string[colon + 1:])
        if "(" in string:
            level = 0
            comma = -1
            inner_string = string[1:last_parenthesis]
            for i, char in enumerate(inner_string):
                if char == "(":
                    level += 1
                elif char == ")":
                    level -= 1
                elif char == "," and level == 0:
                    comma = i
                    break
            if comma != -1: # TODO ELSE?
                node = Node(self.node_counter, Decimal(distance), Decimal(parent.total_distance) + Decimal(distance),
                            parent, bootstrap=string[last_parenthesis + 1:colon])
                self.node_counter += 1
                node.l_child = self.make_node_from_newick(inner_string[:comma], node)
                node.r_child = self.make_node_from_newick(inner_string[comma + 1:], node)
        else:
            node = Node(self.node_counter, Decimal(distance), Decimal(parent.total_distance) + Decimal(distance),
                        parent, name=string[:colon])
            self.node_counter += 1
        return node # TODO

    def in_order(self, root):
        result = []
        if root.l_child:
            result.extend(self.in_order(root.l_child))
        result.append(root)
        if root.r_child:
            result.extend(self.in_order(root.r_child))
        return result

    def to_json(self):
        output = []
        max_distance = 0
        longest_name = ""
        for node in self.in_order(self.root):
            str_id = str(node.id)
            str_distance = str(node.distance)
            str_total_distance = str(node.total_distance)
            if node.parent:
                str_parent = str(node.parent.id)
            else:
                str_parent = ""
            if node.l_child and node.r_child:
                str_l_child = str(node.l_child.id)
                str_r_child = str(node.r_child.id)
            else:
                str_l_child = ""
                str_r_child = ""
            str_name = str(node.name)
            if node.bootstrap:
                str_bootstrap = str(node.bootstrap)
            else:
                str_bootstrap = ""
            output.append({'id': str_id, 'distance': str_distance, 'total_distance': str_total_distance,
                           'parent': str_parent, 'l_child': str_l_child, 'r_child': str_r_child, 'name': str_name,
                           'bootstrap': str_bootstrap})
            if len(str_name) > len(longest_name):
                longest_name = str_name
            if node.total_distance > max_distance:
                max_distance = node.total_distance
        return dumps(output + [{"max_distance": str(max_distance), "longest_name": longest_name}])
