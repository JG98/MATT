# MATT - A Framework For Modifying And Testing Topologies
# Copyright (C) 2021 Jeff Raffael Gower
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
class Node:
    """
    Node class representing nodes on a topology tree
    """

    def __init__(self, id, length, total_length, parent=None, l_child=None, r_child=None, name=None, bootstrap=None):
        """
        Initialises the node
        :param id:
        :param length:
        :param total_length:
        :param parent:
        :param l_child:
        :param r_child:
        :param name:
        :param bootstrap:
        """
        self.id = id
        self.length = length
        self.total_length = total_length
        self.parent = parent
        self.l_child = l_child
        self.r_child = r_child
        self.name = name
        self.bootstrap = bootstrap

# TODO lenghts simultaneously increased via node function
