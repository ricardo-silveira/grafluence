"""
Graph Analytics module
module: graph analytics module
author: ricardosilveira@poli.ufrj.br
"""


class GraphAnalytics(object):
    """
    Methods
    -------
    get_diameter()
        Returns the value of the greatest distance connecting two vertices
    degree_distribution()
        Returns the pdf of vertices degrees
    """
    def __init__(self, **kwargs):
        """
        """
        self.__searcher = kwargs.get("searcher", None)

    def connected_components(self, *args, **kwargs):
        """
        Returns all connected components in the graph

        Parameters
        ----------
        method: object
            Class which will be used for exploring the graph

        Returns
        -------
        list of dicts
            [{Key -> Label for each connected component
             Value -> Lists of vertices of the corresponding component}]
        """
        if not self.__searcher:
            # should raise an exception
            "No searching method defined"
            return []
        root = self.label_map[0]
        c_c = []
        searching_method = method(self)
        trees_list = []
        while searching_method.has_vertices_left():
            trees_list.append(searching_method.explore_graph(root))
            root = searching_method.get_next_vertex()
        component_index = 0
        for spanning_tree in trees_list:
            tree, tree_level = spanning_tree
            vertices = tree.keys()
            vertices_count = len(vertices)
            c_c.append({"index": component_index,
                        "size": vertices_count,
                        "vertices": vertices})
            component_index += 1
        # Sorting components / Bubble sort
        for i in range(len(c_c)):
            for j in range(len(c_c)-i-1):
                if c_c[j]["size"] > c_c[j+1]["size"]:
                    c_c[j], c_c[j+1] = c_c[j+1], c_c[j]
        c_c.reverse()
        return c_c

    def get_diameter(self, method):
        """
        Returns the graph diameter - largest path

        Returns
        -------
        int
            largest distance between a pair of vertices
        """
        diameter = 0
        # Iterating over every vertex
        for v_i in self.index_map.keys():
            searcher = method(self)
            tree, tree_level = searcher.explore_graph(v_i)
            if searcher.has_vertices_left():
                print "More than one connected component, infinite diameter"
                return float("inf")
            # Updating largest distance
            largest_distance = max(tree_level.values())
            if largest_distance > diameter:
                diameter = largest_distance
        return largest_distance

    def degree_distribution(self, *args, **kwargs):
        """
        Computes a Probability Distribution Function of vertices degree
        Returns
        -------
        dict
            PDF represented as {value: frequency}

        Examples
        --------
        Considering the graph for my_graph.txt
        >>> G = Graph(my_graph.txt)
        >>> G.degree_distribution()
        {1: 1.0}
        """
        def update_degree_pdf(degree_pdf, degree, norm):
            try:
                degree_pdf[degree] += 1.0/norm
            except KeyError:
                degree_pdf[degree] = 1.0/norm
        degree_pdf = {}
        #
        avg_degree = 0.0
        for v_i, neighbors in self.edges.iteritems():
            degree = len(neighbors)
            avg_degree += degree
            update_degree_pdf(degree_pdf, degree, self.n_vertices)
        #
        return degree_pdf, avg_degree/self.n_vertices
