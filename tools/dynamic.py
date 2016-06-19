"""
Analyzes graph dynamics
"""


class Dynamic(object):
    """
        !TO-DO
    """
    def __init__(self):
        """
        !TO-DO
        """
        pass

    def graphs_age_diff(self, graph_a, graph_b):
        """
        Method to compare the age difference between two graphs

        Parameters
        ----------
        graph_a: Graph
            Reference graph
        graph_b: Graph
            Compared graph

        Returns
        -------
        dict:
            Adjacency list with all vertices and the time difference for the
            edges to connect to its neighbors from graph_b to graph_a
        """
        ages_graph - {}
        # Iterating over vertices of one graph
        for vertice in graph_a.vertices():
            neighbors = graph_a.get_neighbors(vertice)
            for neighbor in neighbors:
                edge_a_age = graph_a.get_edge(vertice, neighbor)
                edge_b_age = graph_b.get_edge(vertice, neighbor)
                age_diff = float("INF")
                if edge_a_age and edge_b_age:
                    age_diff = edge_b_age - edge_a_age
                if vertice not in ages_graph:
                    ages_graph[vertice] = {}
                ages_graph[vertice][neighbor] = age_diff
        return ages_graph
