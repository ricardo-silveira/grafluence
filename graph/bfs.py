"""
Breadth-First Search module
module: bfs class
author: ricardosilveira@poli.ufrj.br
"""
from explorer import Explorer
from dequeue import Dequeue


class BFS(Explorer):
    """
    Class for operating Breadth-First Search

    Set all vertices as not discovered
    Start from vertice `s`
    Put `s` on queue `Q`
    Set `s` as discovered
    Set the layer counter `i` = 0
    Set the current BFS tree `T` as empty
    While `Q` is not empty
        Initialize an empty list L[i+1]
        For each node `u` in L[i]
            Consider each edge (u,v) incident to `u`
            If `v` is not discovered, then
                Set `v` as discovered
                Add edge (u,v) to the tree `T`
                Add `v` to the list L[i+1]
        Increment the layer counter `i` by one

    (Kleinberg - Tardos: Algorithm Design)
    """

    def explore(self, root, *args, **kwargs):
        """
        Runs breath-first search in the graph and returns two dictionaries
        mapping the generated trees from the search started at vertex `root`
        
        Parameteres
        -----------
        root: int
            vertex label in the graph

        Returns
        -------
        list
            [([dictionary mapping parents in the tree,
              dictionary mapping level of each vertex])]
        """
        vertices_queue = Deque()
        # Put `s` on queue `Q`
        vertices_queue.put(root)
        visited = {}
        # Set `s` as discovered
        visited[root] = True
        # Set the current BFS tree `T` as empty
        tree = {root: None}
        tree_level = {root: 0}
        # While `Q` is not empty
        while not vertices_queue.empty():
            # Gets vertex `u` from the Queue
            v_i = vertices_queue.get_oldest()
            # Removes `u` from list of vertices to visit
            del self.vertices_left[v_i]
            # Consider each edge (u,v) incident to `u`
            for v_j in self.graph.get_neighbors(v_i):
                # If `v` is not discovered, then
                if v_j not in visited:
                    # Add edge (u,v) to the tree `T`
                    tree[v_j] = v_i
                    tree_level[v_j] = tree_level[v_i] + 1
                    # Add vertex `v` to the Queue
                    vertices_queue.put(v_j)
                    # Set `v` as discovered
                    visited[v_j] = True
        return (tree, tree_level)
