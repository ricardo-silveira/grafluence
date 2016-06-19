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
