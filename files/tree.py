from files.node import Node
from json import dumps, loads
from decimal import Decimal, getcontext

getcontext().prec = 10


class Tree:

    def __init__(self, string, from_id=None, to_id=None):
        self.node_counter = 0
        if string[-1] == ";":
            self.from_newick(string[1:-2])
            # TODO PREPARE newick, e.g. remove all \n
        else:
            self.from_json(string, from_id, to_id)

    def from_newick(self, newick):
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
            if self.node_counter <= int(node.get("id")):
                self.node_counter = int(node.get("id")) + 1
        for node in nodes.values():
            if node.parent != "":
                node.parent = nodes[int(node.parent)]
            if node.l_child != "":
                node.l_child = nodes[int(node.l_child)]
            if node.r_child != "":
                node.r_child = nodes[int(node.r_child)]
        self.root = nodes[0]

        # REHANG
        from_node = None
        to_node = None
        for node in nodes.values():
            if node.id == from_id:
                from_node = node
            elif node.id == to_id:
                to_node = node
            else:
                pass  # TODO
        if from_node and to_node:
            from_path = self.find_node(from_node)
            to_path = self.find_node(to_node)
            from_neighbor = None

            # TODO What if from and to are neighbors?
            # TODO What if from has only the root as parent?
            # TODO What if to has no children?
            # TODO What if one is the ancestor of the other?
            from_parent_parent = from_node.parent.parent
            if from_path[-1] == "L":
                from_neighbor = from_node.parent.r_child
            elif from_path[-1] == "R":
                from_neighbor = from_node.parent.l_child
            else:
                pass  # TODO
            from_neighbor.parent = from_parent_parent
            if from_path[-2] == "L":
                from_parent_parent.l_child = from_neighbor
            elif from_path[-2] == "R":
                from_parent_parent.r_child = from_neighbor
            else:
                pass  # TODO

            to_parent = to_node.parent
            distance = Decimal(to_node.distance) / 2
            new_node = Node(from_node.parent.id, distance, Decimal(to_parent.total_distance) + distance, to_parent)
            # new_node = Node(self.node_counter, distance, Decimal(to_parent.total_distance) + distance, to_parent)
            # self.node_counter += 1
            if to_path[-1] == "L":
                to_parent.l_child = new_node
            elif to_path[-1] == "R":
                to_parent.r_child = new_node
            else:
                pass  # TODO
            to_node.parent = new_node
            if to_path < from_path:
                new_node.l_child = to_node
                new_node.r_child = from_node
            elif to_path > from_path:
                new_node.l_child = from_node
                new_node.r_child = to_node
            else:
                pass  # TODO

    def make_node_from_newick(self, string, parent):
        colon = string.rfind(":")
        last_parenthesis = string.rfind(")")
        distance = Decimal(string[colon + 1:])
        node = None
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
            if comma != -1:
                node = Node(self.node_counter, Decimal(distance), Decimal(parent.total_distance) + Decimal(distance),
                            parent, bootstrap=string[last_parenthesis + 1:colon])
                self.node_counter += 1
                node.l_child = self.make_node_from_newick(inner_string[:comma], node)
                node.r_child = self.make_node_from_newick(inner_string[comma + 1:], node)
            else:
                pass  # TODO ?
        else:
            node = Node(self.node_counter, Decimal(distance), Decimal(parent.total_distance) + Decimal(distance),
                        parent, name=string[:colon])
            self.node_counter += 1
        return node  # TODO none?

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

    def get_node(self, string):
        node = self.root
        for char in string:
            if char == "L":
                node = node.l_child
            elif char == "R":
                node = node.r_child
            else:
                pass  # TODO
        return node

    def find_node(self, node):
        string = ""
        while node != self.root:
            if node == node.parent.l_child:
                string = "L" + string
            elif node == node.parent.r_child:
                string = "R" + string
            else:
                pass  # TODO
            node = node.parent
        return string
