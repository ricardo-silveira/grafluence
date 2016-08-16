"""
Graph module
module: graph module
author: ricardosilveira@poli.ufrj.br
"""


class Graph(object):
    """
    Class to represent relations (edges) between objects (vertices) as a graph.

    Attributes
    ----------
    directed
        True for directed edges, False otherwise
    weighted
        True for weighted edges, False otherwise
    n_vertices
        Number of vertices in the graph
    m_edges
        Number of edges in the graph

    Methods
    -------
    parse_graph(file_path)
        Reads graph from file
    add_edge(v_i, v_j, w)
        Adds an edge from v_i to v_j with weight w
    get_neighbors(`vertex`)
        Returns list of neighbors of a given `vertex`
    """
    def __init__(self, **kwargs):
        """
        Setting graph properties

        Parameters
        ----------
        graph_path: str
            Path for text file to parse
        directed: bool
            True if edges are directed, False (default) otherwise
        weighted: bool
            True if edges are weighted, False (default) otherwise
        null_weight: float
            Weight for non-existent edges, 0 (default)
        """
        input_file_path = kwargs.get("graph_path", None)
        self.directed = kwargs.get("directed", False)
        self.weighted = kwargs.get("weighted", False)
        self.null_weight = kwargs.get("null_weight", 0)
        self.edges = {}
        self.n_vertices = None
        self.m_edges = 0
        # Parsing entire graph file
        if input_file_path:
            self.__parse_graph(input_file_path)

    def __parse_graph(self, input_file_path):
        """
        Parses graph file to add edges

        Parameters
        ----------
        input_file_path: str
            Path for graph text file to be parsed
        """
        graph_file = open(input_file_path, "r")
        for edge in graph_file:
            # If number of vertices is unknown
            if not self.n_vertices:
                self.n_vertices = int(edge)
                # Creates structure for adjacency list
                self.edges = self.n_vertices*[self.null_weight]
            # From second line onwards
            else:
                if self.weighted:
                    v_i, v_j, e_w = edge.split(" ")
                else:
                    v_i, v_j = edge.split(" ")
                    e_w = 1.
                # Trying to convert vertices to integers
                try:
                    v_i = int(v_i)
                    v_j = int(v_j)
                # If vertices are strings or anything else
                except ValueError:
                    pass
                e_w = float(e_w)
                self.add_edge(v_i, v_j, e_w)
                # Adding doubled edge
                if not self.directed:
                    self.add_edge(v_j, v_i, e_w)

    def add_edge(self, v_i, v_j, e_w=1.):
        """
        Adds an edge connecting  `v_i` to `v_j` with weight `e_w`

        Parameters
        ----------
        v_i: int
            Vertex index in the graph
        v_j: int
            Vertex index in the graph
        e_w: float
            Weight for the edge connecting `v_i` to `v_j`
        """
        self.m_edges += 1
        try:
            self.edges[v_i][v_j] = e_w
        # First edge of vertex v_i
        except:
            self.edges[v_i] = {v_j: e_w}

    def get_edge(self, v_i, v_j):
        """
        """
        pass

    def get_neighbors(self, v_i):
        """
        Returns all neighbors of vertex `v_i` and the corresponding
        weight of their edges

        Parameters
        ----------
        v_i: object
            label of vertex in the graph

        Returns
        -------
        dict
            Dictionary in which the key is the neighbor vertex and the
            value is the weight of the edge connecting them
        """
        # v_i is same as in the edges structure
        return self.edges[v_i]
