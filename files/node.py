class Node:

    def __init__(self, id, length, total_length, parent=None, l_child=None, r_child=None, name=None, bootstrap=None):
        self.id = id
        self.length = length
        self.total_length = total_length
        self.parent = parent
        self.l_child = l_child
        self.r_child = r_child
        self.name = name
        self.bootstrap = bootstrap

# TODO lenghts simultaneously increased via node function