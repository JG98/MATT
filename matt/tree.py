# MATT - A Framework For Modifying And Testing Topologies
# Copyright (C) 2021-2023 Jeff Raffael Gower
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

# Sets the precision of decimals to 10
getcontext().prec = 10


class Tree:
    """
    Tree class representing a topology tree
    """

    def __init__(self, string, json_args=None, enable_lengths=False):
        """
        Initialises the tree
        :param string: String containing the information about the tree and his nodes
        :param json_args: Further arguments from database if given
        :param enable_lengths: Determines whether branch lengths shall be drawn
        """
        self.node_counter = 0
        self.enable_lengths = enable_lengths
        # Detects a newick file
        if string.rstrip()[-1] == ";":
            self.from_newick(string.rstrip()[1:-2])
            # TODO PREPARE newick, e.g. remove all \n
        else:
            self.from_json(string, json_args)

    def from_newick(self, newick):
        """
        Build a tree from a newick string
        :param newick: the newick string containing the tree info
        :return: None
        """
        self.root = Node(self.node_counter, Decimal(0), Decimal(0))  # TODO BOOTSTRAP FOR EVEN THE FIRST TWO NODES?
        self.node_counter += 1
        level = 0
        # TODO PREPARE newick, e.g. remove all \n
        last_comma = -1
        last_colon = newick.rfind(":")

        # Finds the last comma in the highest level (closest to the root)
        for i, char in enumerate(newick[::-1]):
            if char == "(":
                level += 1
            elif char == ")":
                level -= 1
            elif char == "," and level == 0 and last_comma == -1:
                last_comma = len(newick) - i - 1
                break

        for i, char in enumerate(newick):
            if char == "(":
                level += 1
            elif char == ")":
                level -= 1
            elif char == "," and level == 0:
                # Makes the content left to the comma the left node and vice versa
                if i == last_comma:
                    self.root.l_child = self.make_node_from_newick(newick[:i], self.root)
                    self.root.r_child = self.make_node_from_newick(newick[i + 1:], self.root)
                    return
                # Introduces a new branch if there is three nodes closest to the root
                else:
                    if self.enable_lengths:
                        length = Decimal(newick[last_colon + 1:]) / 2
                    else:
                        length = Decimal(1)
                    self.root.l_child = self.make_node_from_newick(
                        "(" + newick[:last_comma] + "):" + str(length), self.root)
                    if last_colon != -1:
                        self.root.r_child = self.make_node_from_newick(
                            newick[last_comma + 1:last_colon] + ":" + str(length), self.root)
                    else:
                        self.root.r_child = self.make_node_from_newick(
                            newick[last_comma + 1:] + ":" + str(length), self.root)
                    return

    def from_json(self, string, json_args=None):
        """
        Build a tree from a json string
        :param string: the string from the database containing the tree info
        :param json_args: Further information for rehanging or rerooting if given
        :return: None
        """
        print(string)
        print(json_args)
        json = loads(string)
        json.pop()
        nodes = {}

        # Builds node objects from the json string
        for node in json:
            length = node.get("length")
            total_length = node.get("total_length")
            nodes[int(node["id"])] = Node(node.get("id"), Decimal(length), Decimal(total_length),
                                          node.get("parent"), node.get("l_child"), node.get("r_child"),
                                          node.get("name"), node.get("bootstrap"))
            if self.node_counter <= int(node.get("id")):
                self.node_counter = int(node.get("id")) + 1

        # Configures the relationships between the nodes
        for node in nodes.values():
            if node.parent != "":
                node.parent = nodes[int(node.parent)]
            if node.l_child != "":
                node.l_child = nodes[int(node.l_child)]
            if node.r_child != "":
                node.r_child = nodes[int(node.r_child)]
        self.root = nodes[0]

        # Runs when the outgroup or rehang options have been called (relocation of a branch)
        if json_args:
            if len(json_args) == 1:
                # OUTGROUP
                id = json_args[0]

                id_node = None
                for node in nodes.values():
                    if node.id == id:
                        id_node = node

                if id_node:
                    id_path = self.find_node(id_node)

                    # if id_node is on the first level, do not do anything
                    if id_node.parent.id == "0":
                        return

                    lvl_2 = False

                    # if id_node is on the 2nd level, small changes have to be made
                    if id_node.parent.parent.id == "0":
                        lvl_2 = True

                    # id_node becomes new left child of root
                    old_l_child = self.root.l_child
                    self.root.l_child = id_node
                    id_node_parent = id_node.parent
                    if id_path[-1] == "L":
                        id_node_parent.l_child = None
                    elif id_path[-1] == "R":
                        id_node_parent.r_child = None
                    id_node.parent = self.root
                    self.change_children_level(self.root.l_child, -(len(id_path) - 1), True)

                    # id_node's parent becomes new right child of root
                    if not lvl_2:
                        old_r_child = self.root.r_child
                        if id_path[0] == "R":
                            if id_path[1] == "L":
                                old_r_child.l_child = None
                            elif id_path[1] == "R":
                                old_r_child.r_child = None
                        self.root.r_child = id_node_parent
                        next_parent = id_node_parent.parent
                        if id_path[-2] == "L":
                            next_parent.l_child = None
                        elif id_path[-2] == "R":
                            next_parent.r_child = None
                        id_node_parent.parent = self.root
                        self.change_children_level(self.root.r_child, -(len(id_path) - 2), True)
                    else:
                        old_r_child = self.root.r_child

                    # all of id_node's parents fill in the gaps from left to right
                    current_node = self.root.r_child
                    counter = 0
                    for direction in id_path[:2:-1]:
                        counter += 1
                        next_parent_to_be = next_parent.parent
                        if id_path[-2 - counter] == "L":
                            next_parent_to_be.l_child = None
                        elif id_path[-2 - counter] == "R":
                            next_parent_to_be.r_child = None
                        if direction == "L":
                            current_node.l_child = next_parent
                            current_node.l_child.parent = current_node
                            current_node = current_node.l_child
                        elif direction == "R":
                            current_node.r_child = next_parent
                            current_node.r_child.parent = current_node
                            current_node = current_node.r_child
                        next_parent = next_parent_to_be
                        self.change_children_level(current_node, -(len(id_path) - 2 - counter * 2), True)

                    # id_node's upper most ancestor fills the second to last gap
                    if id_path[0] == "L":
                        old_new_node = old_l_child
                        last_node = old_r_child
                    elif id_path[0] == "R":
                        old_new_node = old_r_child
                        last_node = old_l_child

                    if not lvl_2:
                        if id_path[2] == "L":
                            current_node.l_child = old_new_node
                            old_new_node.parent = current_node
                            current_node = current_node.l_child
                        elif id_path[2] == "R":
                            current_node.r_child = old_new_node
                            old_new_node.parent = current_node
                            current_node = current_node.r_child
                        self.change_children_level(current_node, len(id_path) - 2, True)
                    else:
                        self.root.r_child = old_new_node
                        old_new_node.parent = self.root
                        current_node = self.root.r_child

                    # its neighbor fills the last gap
                    if id_path[1] == "L":
                        current_node.l_child = last_node
                        last_node.parent = current_node
                    elif id_path[1] == "R":
                        current_node.r_child = last_node
                        last_node.parent = current_node
                    self.change_children_level(last_node, len(id_path) - 1, True)

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

                    # if len(from_path) < len(to_path):
                    #     tmp_node = to_node
                    #     to_node = from_node
                    #     from_node = tmp_node
                    #
                    #     tmp_path = to_path
                    #     to_path = from_path
                    #     from_path = tmp_path

                    difference = len(to_path) - len(from_path)

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

                        # to_node.length = Decimal(to_node.length + 1)
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
                            self.change_children_level(from_node.l_child, 1 + difference, True)
                        if from_node.r_child:
                            self.change_children_level(from_node.r_child, 1 + difference, True)

            else:
                pass  # TODO

    def make_node_from_newick(self, string, parent):
        """
        Helper function to build nodes from newick files
        :param string: the string containing information about the current node in the recursion
        :param parent: the parent node calling this function
        :return: the newly created node
        """
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
            if colon != -1:
                node = Node(self.node_counter, length, total_length, parent, name=string[:colon])
            else:
                node = Node(self.node_counter, length, total_length, parent, name=string)
            self.node_counter += 1
        return node  # TODO none?

    def in_order(self, root):
        """
        Traverses the tree in in-order and saves the result in a list
        :param root: the node where traversal should start
        :return: list of nodes
        """
        result = []
        if root.l_child:
            result.extend(self.in_order(root.l_child))
        result.append(root)
        if root.r_child:
            result.extend(self.in_order(root.r_child))
        return result

    def to_json(self):
        """
        Dumps the tree info to a json string
        :return: json
        """
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
        return dumps(output + [
            {"enable_lengths": self.enable_lengths, "max_length": str(max_length), "longest_name": longest_name}])

    def to_newick(self, as_constraint=False):
        """
        Returns the tree in newick format
        :param as_constraint: determines whether only simple information should be added
        :return: newick string
        """
        return self.newick_helper(self.root, as_constraint) + ";\n"

    def newick_helper(self, root, as_constraint=False):
        """
        Helper function for building the newick tree
        :param root: the root node to start from in the current recursion
        :param as_constraint: determines whether only simple information should be added
        :return: newick string
        """
        result = ""
        if root.l_child and root.r_child:
            result += "(" + self.newick_helper(root.l_child, as_constraint) + "," + self.newick_helper(root.r_child,
                                                                                                       as_constraint) + ")"
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
        """
        Changes the level of a node after rehanging or rerooting
        :param node: the node to change
        :param amount: the amount of levels that should be added (or removed when negative)
        :param total_only: determines whether only the total length should be altered
        :return: None
        """
        if not total_only:
            node.length = Decimal(node.length + amount)
        node.total_length = Decimal(node.total_length + amount)
        if node.l_child:
            self.change_children_level(node.l_child, amount, total_only)
        if node.r_child:
            self.change_children_level(node.r_child, amount, total_only)

    def find_node(self, node):
        """
        Returns a string explaining the path from the root to given node
        :param node: the node to search
        :return: path to node from root
        """
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
        """
        Returns a node for given path
        :param path: path to node
        :return: found node
        """
        node = self.root
        for c in path:
            if c == "L":
                node = node.l_child
            elif c == "R":
                node = node.r_child
            else:  # TODO
                pass
        return node
