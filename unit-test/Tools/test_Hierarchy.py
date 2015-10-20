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

import unittest

####################################################################################################

from FinancialSimulator.Tools.Hierarchy import Node, Hierarchy

####################################################################################################

class MyNode(Node):

    ##############################################

    def __init__(self, number, parent=None):

        super(MyNode, self).__init__(parent)
        self._number = number

    ##############################################

    def __repr__(self):

        return 'Node {}'.format(self._number)

    ##############################################

    def __hash__(self):

        return self._number

    ##############################################

    def __lt__(self, other):

        return self._number < other._number

####################################################################################################

class TestNode(unittest.TestCase):

    def test(self):

        node_1 = MyNode(1)
        node_11 = MyNode(11, parent=node_1)
        node_111 = MyNode(111, parent=node_11)
        node_13 = MyNode(13, parent=node_1)
        node_131 = MyNode(131, parent=node_13)
        node_1312 = MyNode(1312, parent=node_131)
        node_1311 = MyNode(1311, parent=node_131)
        node_12 = MyNode(12, parent=node_1)
        node_121 = MyNode(121, parent=node_12)
        node_14 = MyNode(14, parent=node_1)
        node_141 = MyNode(141, parent=node_14)

        for node in node_1.depth_first_search_sibling():
            node.sort_siblings()
        flat_list = [node for node in node_1.depth_first_search()]
        flat_list_true = [
            node_1,
            node_11, node_111,
            node_12, node_121,
            node_13, node_131, node_1311, node_1312,
            node_14, node_141,
        ]
        self.assertListEqual(flat_list, flat_list_true)

####################################################################################################

class TestHierarchy(unittest.TestCase):

    def test(self):

        node_1 = MyNode(1)
        node_11 = MyNode(11, parent=node_1)
        node_2 = MyNode(2)
        node_21 = MyNode(21, parent=node_2)
        node_3 = MyNode(3)
        node_31 = MyNode(31, parent=node_3)

        hierarchy = Hierarchy()
        for node in (node_1, node_2, node_3):
            hierarchy.add_node(node)
        flat_list = [node for node in hierarchy]
        flat_list_true = [
            node_1, node_11,
            node_2, node_21,
            node_3, node_31,
        ]
        self.assertListEqual(flat_list, flat_list_true)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
