from files.node import Node
from re import findall
from json import dumps
from decimal import Decimal, getcontext


class Tree:

    # Shoutout to trincot at https://stackoverflow.com/a/51375562
    # Change this to the opposite of the reverse
    def __init__(self, newick):
        getcontext().prec = 10
        self.l_root = None
        self.r_root = None
        tokens = findall(r"([^:;,()\s]*)(?:\s*:\s*([\d.]+)\s*)?([,);])|(\S)", newick)

        def recurse(next_id=0, parent_id=-1):
            current_id = next_id
            children = []

            name, distance, delimiter, parenthesis = tokens.pop(0)
            if parenthesis == "(":
                while parenthesis in "(,":
                    node, parenthesis, next_id = recurse(next_id + 1, current_id)
                    children.append(node)
                name, distance, delimiter, parenthesis = tokens.pop(0)
            return {"id": current_id, "name": name, "distance": Decimal(distance) if distance else None,
                    "parent_id": parent_id, "children": children}, delimiter, next_id

        result = recurse()[0]["children"]
        nodes = []
        while result:
            new_result = result.copy()
            for node in new_result:
                children = node.pop("children")
                nodes.append(node)
                result.remove(node)
                if children:
                    result.extend(children)

        if not nodes[3].get("parent_id") == 0:
            pass #do

        previous_layer = {}
        current_layer = {}

        for node in nodes:
            id = node.get("id")
            distance = node.get("distance")
            if node.get("parent_id") == 0:
                if node.get("name"):
                    current_node = Node(id, Decimal(distance), Decimal(distance), name=node.get("name"))
                else:
                    current_node = Node(id, Decimal(distance), Decimal(distance))
                if not self.l_root:
                    self.l_root = current_node
                else:
                    self.r_root = current_node
                current_layer[node.get("id")] = current_node
                continue
            if not node.get("parent_id") in previous_layer:
                previous_layer.clear()
                previous_layer = current_layer.copy()
                current_layer.clear()
            parent = previous_layer.get(node.get("parent_id"))
            if node.get("name"):
                current_node = Node(id, distance, Decimal(parent.total_distance) + Decimal(distance), parent, name=node.get("name"))
            else:
                current_node = Node(id, distance, Decimal(parent.total_distance) + Decimal(distance), parent)
            if not parent.l_child:
                parent.l_child = current_node
            else:
                parent.r_child = current_node
            current_layer[node.get("id")] = current_node

    def in_order(self, root):
        result = []
        if root.l_child:
            result.extend(self.in_order(root.l_child))
        result.append(root)
        if root.r_child:
            result.extend(self.in_order(root.r_child))
        return result

    def pre_order(self, root):
        result = [root]
        if root.l_child:
            result.extend(self.pre_order(root.l_child))
        if root.r_child:
            result.extend(self.pre_order(root.r_child))
        return result

    def to_json(self, order):
        if order == "in":
            ordered_list = self.in_order(self.l_root) + [Node(0, 0, 0)] + self.in_order(self.r_root)
        elif order == "pre":
            ordered_list = Node(0, 0, 0) + self.pre_order(self.l_root) + self.pre_order(self.r_root)
        output = []
        counter = 0
        for node in ordered_list:
            output.append({'id': str(node.id), 'name': str(node.name), 'total_distance': str(node.total_distance), 'counter': counter})
            counter += 1
        return dumps(output)
        #sorted(output.items(), key=lambda out: (out[1], out[0]))
