from files.node import Node
from json import dumps, loads
from decimal import Decimal, getcontext

getcontext().prec = 10


class Tree:

    def __init__(self, string, json_args=None, enable_distances=False):
        self.node_counter = 0
        self.enable_distances = enable_distances
        if string[-1] == ";":  # TODO POTENTIAL ERROR SOURCE
            self.from_newick(string.rstrip()[1:-2])
            # TODO PREPARE newick, e.g. remove all \n
        else:
            self.from_json(string, json_args)

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
                    if self.enable_distances:
                        distance = Decimal(newick[last_colon + 1:]) / 2
                    else:
                        distance = Decimal(1)
                    self.root.l_child = self.make_node_from_newick(
                        "(" + newick[:last_comma] + "):" + str(distance), self.root)
                    self.root.r_child = self.make_node_from_newick(
                        newick[last_comma+1:last_colon] + ":" + str(distance), self.root)
                    return

    def from_json(self, string, json_args=None):
        json = loads(string)
        json.pop()
        nodes = {}
        for node in json:
            distance = node.get("distance")
            total_distance = node.get("total_distance")
            nodes[int(node["id"])] = Node(node.get("id"), Decimal(distance), Decimal(total_distance),
                                          node.get("parent"), node.get("l_child"), node.get("r_child"),
                                          node.get("name"), node.get("bootstrap"))
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

        if json_args:
            # TODO reroot and rehang have much in common, change this!
            if len(json_args) == 1:
                #REROOT
                id = json_args[0]

                id_node = None
                for node in nodes.values():
                    if node.id == id:
                        id_node = node

                if id_node:
                    id_path = self.find_node(id_node)

                    if id_node.parent.id == "0":
                        return

                if id_path[-1] == "L":
                    id_node.parent.l_child = None
                elif id_path[-1] == "R":
                    id_node.parent.r_child = None

                id_parent_parent = id_node.parent.parent
                if id_path[-1] == "L":
                    id_neighbor = id_node.parent.r_child
                elif id_path[-1] == "R":
                    id_neighbor = id_node.parent.l_child

                id_neighbor.parent = id_parent_parent
                if id_path[-2] == "L":
                    id_parent_parent.l_child = id_neighbor
                elif id_path[-2] == "R":
                    id_parent_parent.r_child = id_neighbor

                # TODO ELSE
                if not self.enable_distances:
                    new_node = Node(id_node.parent.id, Decimal(1), Decimal(1), self.root, self.root.l_child, self.root.r_child)
                    self.root.l_child = id_node
                    self.root.r_child = new_node
                    id_node.distance = Decimal(1)
                    id_node.total_distance = Decimal(1)
                    self.change_children_level(new_node.l_child, 1)
                    self.change_children_level(new_node.r_child, 1)
                    if id_neighbor:  # TODO necessary?
                        self.change_children_level(id_neighbor, -1)

            elif len(json_args) == 2:
                # REHANG
                from_id = json_args[0]
                to_id = json_args[1]

                from_node = None
                to_node = None
                for node in nodes.values():
                    if node.id == from_id:
                        from_node = node
                    elif node.id == to_id:
                        to_node = node

                if from_node and to_node:
                    from_path = self.find_node(from_node)
                    to_path = self.find_node(to_node)

                    if (from_node.parent.id == "0" and to_node.parent.id == "0") or \
                            (len(from_path) == len(to_path) and from_path[-2] == to_path[-2]):
                        return

                    if len(from_path) < len(to_path):
                        tmp_node = to_node
                        to_node = from_node
                        from_node = tmp_node

                        tmp_path = to_path
                        to_path = from_path
                        from_path = tmp_path

                    if from_path[-1] == "L":
                        from_node.parent.l_child = None
                    elif from_path[-1] == "R":
                        from_node.parent.r_child = None

                    from_parent_parent = from_node.parent.parent
                    if from_path[-1] == "L":
                        from_neighbor = from_node.parent.r_child
                    elif from_path[-1] == "R":
                        from_neighbor = from_node.parent.l_child

                    from_neighbor.parent = from_parent_parent
                    if from_path[-2] == "L":
                        from_parent_parent.l_child = from_neighbor
                    elif from_path[-2] == "R":
                        from_parent_parent.r_child = from_neighbor

                    to_parent = to_node.parent
                    if self.enable_distances:
                        distance = Decimal(to_node.distance) / 2
                        total_distance = Decimal(to_parent.total_distance) + distance
                    else:
                        distance = Decimal(to_node.distance)
                        total_distance = Decimal(to_parent.total_distance) + distance

                        to_node.distance = Decimal(to_node.distance + 1)
                        to_node.total_distance = Decimal(to_node.total_distance + 1)

                        from_node.distance = Decimal(to_node.distance)
                        from_node.total_distance = Decimal(to_node.total_distance)
                    # TODO REMINDER THIS IS THE NEW PARENT IN BETWEEN
                    new_node = Node(from_node.parent.id, distance, total_distance, to_parent)
                    # new_node = Node(self.node_counter, distance, total_distance, to_parent)
                    # self.node_counter += 1
                    if to_path[-1] == "L":
                        to_parent.l_child = new_node
                    elif to_path[-1] == "R":
                        to_parent.r_child = new_node
                    to_node.parent = new_node
                    if to_path < from_path:
                        new_node.l_child = to_node
                        new_node.r_child = from_node
                    elif to_path > from_path:
                        new_node.l_child = from_node
                        new_node.r_child = to_node
                    if not self.enable_distances:
                        # all ancestors from from to the left
                        # all descendants from to to the right
                        if to_node.l_child:
                            self.change_children_level(to_node.l_child, 1)
                        if to_node.r_child:
                            self.change_children_level(to_node.r_child, 1)
                        if from_neighbor: # TODO necessary?
                            self.change_children_level(from_neighbor, -1)
            else:
                pass #TODO

    def make_node_from_newick(self, string, parent):
        colon = string.rfind(":")
        last_parenthesis = string.rfind(")")
        if self.enable_distances:
            distance = Decimal(string[colon + 1:])
        else:
            distance = Decimal(1)
        total_distance = Decimal(parent.total_distance) + Decimal(distance)
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
                node = Node(self.node_counter, distance, total_distance, parent,
                            bootstrap=string[last_parenthesis + 1:colon])
                self.node_counter += 1
                node.l_child = self.make_node_from_newick(inner_string[:comma], node)
                node.r_child = self.make_node_from_newick(inner_string[comma + 1:], node)
            else:
                pass  # TODO ?
        else:
            node = Node(self.node_counter, distance, total_distance, parent, name=string[:colon])
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
            if str_name != "None" and (len(str_name) > len(longest_name)):
                longest_name = str_name
            if node.total_distance > max_distance:
                max_distance = node.total_distance
        return dumps(output + [{"enable_distances": self.enable_distances, "max_distance": str(max_distance), "longest_name": longest_name}])

    def to_newick(self):
        return self.newick_helper(self.root)[:-2] + ";"

    def newick_helper(self, root):
        result = ""
        if root.l_child and root.r_child:
            result += "(" + self.newick_helper(root.l_child) + "," + self.newick_helper(root.r_child) + ")"
            if root.bootstrap:
                result += root.bootstrap
            result += ":" + str(root.distance)
        else:
            result += root.name + ":" + str(root.distance)
        return result

    # TODO overhaul, does not require this much
    def change_children_level(self, node, amount):
        node.distance = Decimal(node.distance + amount)
        node.total_distance = Decimal(node.total_distance + amount)
        if node.l_child:
            self.change_children_level(node.l_child, amount)
        if node.r_child:
            self.change_children_level(node.r_child, amount)

    '''def get_node(self, string):
        node = self.root
        for char in string:
            if char == "L":
                node = node.l_child
            elif char == "R":
                node = node.r_child
            else:
                pass  # TODO
        return node'''

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
