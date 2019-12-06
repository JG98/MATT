from files.node import Node
from re import findall
from json import dumps
from decimal import Decimal, getcontext


class Tree:

    # Shoutout to trincot at https://stackoverflow.com/a/51375562
    # Change this to the opposite of the reverse
    def __init__(self, newick):
        getcontext().prec = 10
        self.root = Node(0, 0, Decimal(0))

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

        if len(result) == 3:
            level = 0
            commas = 0
            counter = 0
            position = 0
            last_colon = 0
            new_newick = newick[1:-2]
            for char in new_newick:
                if char == "(":
                    level += 1
                elif char == ")":
                    level -= 1
                elif char == "," and level == 0:
                    commas += 1
                    if commas == 2:
                        position = counter - 1
                elif char == ":" and level == 0:
                    last_colon = counter
                counter += 1
            length = Decimal(new_newick[last_colon + 1:-2])
            new_newick = "((" + new_newick[:position + 1] + "):" + str(Decimal(length/2)) + new_newick[position + 1:last_colon] + ":" + str(Decimal(length/2)) + ");"
            tokens = findall(r"([^:;,()\s]*)(?:\s*:\s*([\d.]+)\s*)?([,);])|(\S)", new_newick)
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
                if not self.root.l_child:
                    self.root.l_child = current_node
                else:
                    self.root.r_child = current_node
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
        self.by_level = nodes

        def in_order(root):
            result = []
            if root.l_child:
                result.extend(in_order(root.l_child))
            result.append(root)
            if root.r_child:
                result.extend(in_order(root.r_child))
            return result

        self.by_order = in_order(self.root)

    def to_json(self):
        output = []
        max_distance = 0
        longest_name = 0
        for node in self.by_order:
            if node.l_child and node.r_child:
                output.append({'id': str(node.id), 'name': str(node.name), 'total_distance': str(node.total_distance), 'l_child': str(node.l_child.id), 'r_child': str(node.r_child.id)})
            else:
                output.append({'id': str(node.id), 'name': str(node.name), 'total_distance': str(node.total_distance)})
                if len(node.name) > longest_name:
                    longest_name = len(node.name)
            if node.total_distance > max_distance:
                max_distance = node.total_distance
        return dumps(output + [{"max_distance": str(max_distance), "longest_name": str(longest_name)}])
        #sorted(output.items(), key=lambda out: (out[1], out[0]))
