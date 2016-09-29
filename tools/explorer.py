"""
Abstract class for methods that wil explore graph
module: searcher module
author: ricardosilveira@poli.ufrj.br
"""


class Explorer(object):

    def __init__(self, graph, *kwargs):
        """
        Copies all vertices from graph and stores it in a dictionary
        """
        vertices_list = graph.indexes_map.keys()
        self.graph = graph
        self.vertices_left = {}
        for vertex in vertices_list:
            self.vertices_left[vertex] = None
    
    def has_vertices_left(self):
        """
        Returns True if there are vertices not market yet
        False if all vertices were discovered already
        """
        return len(self.vertices_left.keys()) > 0

    def get_next_vertex(self):
        """
        Returns the first available vertex in vertices_left
        or none if none is available
        """
        try:
            return self.vertices_left.keys()[0]
        except IndexError:
            return None
    
    def from_i_to_root(self, tree, vertex_name):
        """
        Returns
        -------
        list
            Elements in path from element i to root
        """
        path = []
        start_node = self.graph.vertices_map[vertex_name]
        current_node_index = start_node
        while tree[current_node_index] != None:
            current_node_index = self.graph.vertices_map[tree[current_node_index]]
            path.append(self.graph.indexes_map[current_node_index])
        #path.append(self.graph.indexes_map[current_node_index])
        return path
    
    def neighbors_in_tree(self, tree, vertex_index):
        """
        Finds neighbors of a vertex in the spanning tree
        
        Parameters
        ----------
        tree: list
            list representing spanning tree, in which each element
            points to its precessor in the tree
        vertex_index:
            element which we wish to find its neighbors
        """
        neighbors = []
        for i in range(len(tree)):
            if tree[i] == vertex_index:
                neighbors.append(i)
        neighbors.append(tree[vertex_index])
        return neighbors

    def export_spanning_tree(self, spanning_tree, output_path, mapped=True):
        """
        Needs to be improved... But it is supposed to print the spanning tree
        """
        with open(output_path, "w+") as output_file:
            tree_size = len(spanning_tree)-1
            count = 0
            printed = []
            for v_i in xrange(tree_size, -1, -1):
                leaf = self.graph.indexes_map[v_i]
                while not spanning_tree[v_i] is None:
                    v_j = spanning_tree[v_i]
                    if mapped:
                        v_j = self.graph.vertices_map[v_j]
                    v_i = v_j
                    ouput_file.write(str(leaf)+" "+str(G.indexes_map[v_i]))
