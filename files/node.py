class Node:

    def __init__(self, id, distance, total_distance, parent=None, l_child=None, r_child=None, name=None, bootstrap=None):
        self.id = id
        self.distance = distance
        self.total_distance = total_distance
        self.parent = parent
        self.l_child = l_child
        self.r_child = r_child
        self.name = name
        self.bootstrap = bootstrap

# TODO distances simultaneously increased via node function