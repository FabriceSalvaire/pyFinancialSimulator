####################################################################################################
#
# pyFinancialSimulator - A Financial Simulator
# Copyright (C) 2015 Fabrice Salvaire
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

class Leaf:

    ##############################################

    def __init__(self, parent=None):

        self._parent = parent
        if parent is not None:
            parent.add_sibling(self)

    ##############################################

    @property
    def parent(self):
        return self._parent

    ##############################################

    def is_leaf(self):
        return True

    ##############################################

    def has_siblings(self):
        return False

    ##############################################

    def __iter__(self):
        # Fixme:
        return iter([])

    ##############################################

    def depth_first_search(self):

        yield self

    ##############################################

    def depth_first_search_sibling(self):

        yield self

####################################################################################################

class Node(Leaf):

    ##############################################

    def __init__(self, parent=None, siblings=None):

        super().__init__(parent)
        if siblings is not None:
            self._siblings = list(siblings)
        else:
            self._siblings = []

    ##############################################

    @property
    def siblings(self):
        # Fixme: to protect
        return iter(self._siblings)

    ##############################################

    def is_leaf(self):
        return False

    ##############################################

    def has_siblings(self):
        return True

    ##############################################

    def __iter__(self):
        return iter(self._siblings)

    ##############################################

    def add_sibling(self, sibling):

        if sibling not in self._siblings:
            self._siblings.append(sibling)
        else:
            raise NameError("Sibling {} is already registered".format(sibling))

    ##############################################

    def sort_siblings(self):

        self._siblings.sort()

    ##############################################

    def depth_first_search(self):

        yield self
        for sibling in self._siblings:
            yield from sibling.depth_first_search()

    ##############################################

    def depth_first_search_sibling(self):

        for sibling in self._siblings:
            yield from sibling.depth_first_search_sibling()
        yield self

####################################################################################################

class NonExistingNodeError(Exception):
    pass

####################################################################################################

class Hierarchy:

    ##############################################

    def __init__(self):

        self._nodes = {}
        self._root_nodes = []

    ##############################################

    def add_node(self, node):

        node_hash = hash(node)
        if node_hash not in self._nodes:
            self._nodes[node_hash] = node
        else:
            raise NameError("Node {} is already registered".format(node_hash))
        
        if node.parent is None:
            self._root_nodes.append(node)

    ##############################################

    def add_node_recursive(self, node):

        # Node hierarchy must not change !
        for node in node.depth_first_search():
            self.add_node(node)

    ##############################################

    def sort(self):

        self._root_nodes.sort()

    ##############################################

    def __getitem__(self, node_hash):

        try:
            return self._nodes[node_hash]
        except KeyError:
            raise NonExistingNodeError(node_hash)

    ##############################################

    def __iter__(self):

        for root_node in self._root_nodes:
            yield from root_node.depth_first_search()

####################################################################################################
#
# End
#
####################################################################################################
