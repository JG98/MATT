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

from matt.node import Node
from json import dumps, loads
from decimal import Decimal, getcontext

getcontext().prec = 10


class Tree:

    def __init__(self, string, json_args=None, enable_lengths=False):
        self.node_counter = 0
        self.enable_lengths = enable_lengths
        if string.rstrip()[-1] == ";":
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
                    if self.enable_lengths:
                        length = Decimal(newick[last_colon + 1:]) / 2
                    else:
                        length = Decimal(1)
                    self.root.l_child = self.make_node_from_newick(
                        "(" + newick[:last_comma] + "):" + str(length), self.root)
                    self.root.r_child = self.make_node_from_newick(
                        newick[last_comma+1:last_colon] + ":" + str(length), self.root)
                    return

    def from_json(self, string, json_args=None):
        print(string)
        print(json_args)
        json = loads(string)
        json.pop()
        nodes = {}
        for node in json:
            length = node.get("length")
            total_length = node.get("total_length")
            nodes[int(node["id"])] = Node(node.get("id"), Decimal(length), Decimal(total_length),
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
            if len(json_args) == 1:
                #OUTGROUP
                id = json_args[0]

                id_node = None
                for node in nodes.values():
                    if node.id == id:
                        id_node = node

                if id_node:
                    id_path = self.find_node(id_node)

                    if id_node.parent.id == "0":
                        return

                self.outgroup_helper(self.root, id_path)

                # if id_path[-1] == "L":
                #     id_node.parent.l_child = None
                # elif id_path[-1] == "R":
                #     id_node.parent.r_child = None
                #
                # id_parent_parent = id_node.parent.parent
                # if id_path[-1] == "L":
                #     id_neighbor = id_node.parent.r_child
                # elif id_path[-1] == "R":
                #     id_neighbor = id_node.parent.l_child
                #
                # id_neighbor.parent = id_parent_parent
                # if id_path[-2] == "L":
                #     id_parent_parent.l_child = id_neighbor
                # elif id_path[-2] == "R":
                #     id_parent_parent.r_child = id_neighbor
                #
                # # TODO ELSE
                # if not self.enable_lengths:
                #     new_node = Node(id_node.parent.id, Decimal(1), Decimal(1), self.root, self.root.l_child, self.root.r_child)
                #     self.root.l_child = id_node
                #     self.root.r_child = new_node
                #     new_node.l_child.parent = new_node
                #     new_node.r_child.parent = new_node
                #     id_node.length = Decimal(1)
                #     id_node.total_length = Decimal(1)
                #     self.change_children_level(new_node.l_child, 1, True)
                #     self.change_children_level(new_node.r_child, 1, True)
                #     if id_neighbor:  # TODO necessary?
                #         self.change_children_level(id_neighbor, -1, True)
                #
                # id_node.parent = self.root

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
                    if self.enable_lengths:
                        length = Decimal(to_node.length) / 2
                        total_length = Decimal(to_parent.total_length) + length
                    else:
                        length = Decimal(to_node.length)
                        total_length = Decimal(to_parent.total_length) + length

                        #to_node.length = Decimal(to_node.length + 1)
                        to_node.total_length = Decimal(to_node.total_length + 1)

                        from_node.length = Decimal(to_node.length)
                        from_node.total_length = Decimal(to_node.total_length)
                    # TODO REMINDER THIS IS THE NEW PARENT IN BETWEEN
                    new_node = Node(from_node.parent.id, length, total_length, to_parent)
                    # new_node = Node(self.node_counter, length, total_length, to_parent)
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
                    if not self.enable_lengths:
                        # all ancestors from from to the left
                        # all descendants from both to the right
                        if to_node.l_child:
                            self.change_children_level(to_node.l_child, 1)
                        if to_node.r_child:
                            self.change_children_level(to_node.r_child, 1)
                        if from_neighbor:  # TODO necessary?
                            self.change_children_level(from_neighbor, -1, True)
                        if from_node.l_child:
                            self.change_children_level(from_node.l_child, 1, True)
                        if from_node.r_child:
                            self.change_children_level(from_node.r_child, 1, True)
            else:
                pass  # TODO

    def make_node_from_newick(self, string, parent):
        colon = string.rfind(":")
        last_parenthesis = string.rfind(")")
        if self.enable_lengths:
            length = Decimal(string[colon + 1:])
        else:
            length = Decimal(1)
        total_length = Decimal(parent.total_length) + Decimal(length)
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
                node = Node(self.node_counter, length, total_length, parent,
                            bootstrap=string[last_parenthesis + 1:colon])
                self.node_counter += 1
                node.l_child = self.make_node_from_newick(inner_string[:comma], node)
                node.r_child = self.make_node_from_newick(inner_string[comma + 1:], node)
            else:
                pass  # TODO ?
        else:
            node = Node(self.node_counter, length, total_length, parent, name=string[:colon])
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
        max_length = 0
        longest_name = ""
        for node in self.in_order(self.root):
            str_id = str(node.id)
            str_length = str(node.length)
            str_total_length = str(node.total_length)
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
            output.append({'id': str_id, 'length': str_length, 'total_length': str_total_length,
                           'parent': str_parent, 'l_child': str_l_child, 'r_child': str_r_child, 'name': str_name,
                           'bootstrap': str_bootstrap})
            if str_name != "None" and (len(str_name) > len(longest_name)):
                longest_name = str_name
            if node.total_length > max_length:
                max_length = node.total_length
        return dumps(output + [{"enable_lengths": self.enable_lengths, "max_length": str(max_length), "longest_name": longest_name}])

    def to_newick(self, as_constraint=False):
        return self.newick_helper(self.root, as_constraint) + ";\n"

    def newick_helper(self, root, as_constraint=False):
        result = ""
        if root.l_child and root.r_child:
            result += "(" + self.newick_helper(root.l_child, as_constraint) + "," + self.newick_helper(root.r_child, as_constraint) + ")"
            if not as_constraint:
                if root.bootstrap:
                    result += root.bootstrap
                if self.enable_lengths:
                    result += ":" + str(root.length)
        else:
            result += root.name
            if not as_constraint and self.enable_lengths:
                result += ":" + str(root.length)
        return result

    # TODO overhaul, does not require this much
    def change_children_level(self, node, amount, total_only=False):
        if not total_only:
            node.length = Decimal(node.length + amount)
        node.total_length = Decimal(node.total_length + amount)
        if node.l_child:
            self.change_children_level(node.l_child, amount, total_only)
        if node.r_child:
            self.change_children_level(node.r_child, amount, total_only)

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

    def get_node(self, path):
        node = self.root
        for c in path:
            if c == "L":
                node = node.l_child
            elif c == "R":
                node = node.r_child
            else:  # TODO
                pass
        return node

    def outgroup_helper(self, node, id_path):
        # TODO LENGTH HANDLING WHEN LENGTHS ARE NOT DISABLED

        l_child = node.l_child
        r_child = node.r_child
        l_path = self.find_node(l_child)
        r_path = self.find_node(r_child)

        level = len(l_path) - 1

        if l_path == id_path or r_path == id_path:
            return

        swap_node = self.get_node(id_path)
        if level > 0:
            current_node = swap_node
            for i in range(1, level):
                current_node = current_node.parent
            if current_node.parent.l_child == current_node:
                swap_node = current_node.parent.r_child
            else:
                swap_node = current_node.parent.l_child
        swap_path = self.find_node(swap_node)
        swap_level = len(swap_path) - 1

        if id_path[level] == "R":
            tmp_node = swap_node.parent
            swap_node.parent = node
            l_child.parent = tmp_node
            node.l_child = swap_node
            if swap_path[-1] == "L":
                tmp_node.l_child = l_child
            else:
                tmp_node.r_child = l_child
            if not self.enable_lengths:
                self.change_children_level(node.l_child, -(swap_level - level), True)
                self.change_children_level(l_child, (swap_level - level), True)
            if r_child:
                self.outgroup_helper(r_child, id_path)
        elif id_path[level] == "L":
            tmp_node = swap_node.parent
            swap_node.parent = node
            r_child.parent = tmp_node
            node.r_child = swap_node
            if swap_path[-1] == "L":
                tmp_node.l_child = r_child
            else:
                tmp_node.r_child = r_child
            if not self.enable_lengths:
                self.change_children_level(node.r_child, -(swap_level - level), True)
                self.change_children_level(r_child, (swap_level - level), True)
            if l_child:
                self.outgroup_helper(l_child, id_path)
        return
