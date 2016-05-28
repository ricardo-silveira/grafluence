
"""
Graph module
module: graph module
author: ricardosilveira@poli.ufrj.br
"""
import numpy as np


ADJ_LIST = "adj_list"
ADJ_MATRIX = "adj_matrix"


class Graph(object):
    """
    Class to represent relations (edges) between objects (vertices) as a graph.

    Attributes
    ----------
    directed
        True for directed edges, False otherwise
    weighted
        True for weighted edges, False otherwise
    structure
        'adj_list' if edges will be represented as an adjacency_list
        'adj_matrix' if edges will be represented as an adjacency_matrix
    n_vertices
        Number of vertices in the graph
    m_edges
        Number of edges in the graph
    indexes_map
        Mapping vertices labels and their corresponding index in the graph
    vertices_map
        Mapping vertices indices and their corresponding label in the graph

    Methods
    -------
    parse_graph(file_path)
        Reads graph from file
    add_edge(v_i, v_j, w)
        Adds an edge from v_i to v_j with weight w
    get_neighbors(`vertex`)
        Returns list of neighbors of a given `vertex`
    connected_components()
        Returns connected components of a graph
    degree_distribution()
        Returns the pdf of vertices degrees
    get_diameter()
        Returns the value of the greatest distance connecting two vertices
    get_vertex_index()
        Returns index in data structure
    export_graph_info()
        Writes relevant graph info to file
    label_to_vertices(label_path)
        Adds label to vertices from file at label_path
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
        structure: str
            'adj_list' (default) for adjacency list graph representation
            'adj_matrix' for adjacency matrix graph representation
        """
        input_file_path = kwargs.get("graph_path", None)
        self.directed = kwargs.get("directed", False)
        self.weighted = kwargs.get("weighted", False)
        self.null_weight = kwargs.get("null_weight", 0)
        self.structure = kwargs.get("structure", ADJ_LIST)
        # Key -> vertice in graph file
        # Value -> vertice index in graph
        self.vertices_map = {}
        self.indexes_map = {}
        self.__vertex_index = 0
        self.n_vertices = None
        self.m_edges = 0
        # Parsing entire graph file
        if input_file_path:
            self.parse_graph(input_file_path)

    def parse_graph(self, input_file_path):
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
                if self.structure == ADJ_LIST:
                    self.edges = self.n_vertices*[self.null_weight]
                # Creates sctructure for adjacency matrix
                elif self.structure == ADJ_MATRIX:
                    self.edges = np.full((self.n_vertices, self.n_vertices),
                                          self.null_weight)
                else:
                    raise ValueError("Invalid graph structure")
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
        if self.edges is None:
            raise ValueError("No structure type defined")
        # Indexes for vertices v_i and v_j in graph
        mapped_v_i = self.get_vertex_index(v_i)
        mapped_v_j = self.get_vertex_index(v_j)
        self.m_edges += 1
        if self.structure == ADJ_LIST:
            try:
                self.edges[mapped_v_i][mapped_v_j] = e_w
            # First edge of vertex v_i
            except:
                self.edges[mapped_v_i] = {mapped_v_j: e_w}
        if self.structure == ADJ_MATRIX:
            self.edges[mapped_v_i, mapped_v_j] = e_w

    def get_neighbors(self, v_i, **kwargs):
        """
        Returns all neighbors of vertex `v_i` and the corresponding
        weight of their edges

        Parameters
        ----------
        v_i: object
            label of vertex in the graph
        mapped: bool
            True if v_i is already mapped, False otherwise (default)

        Returns
        -------
        dict
            Dictionary in which the key is the neighbor vertex and the
            value is the weight of the edge connecting them
        """
        mapped = kwargs.get("mapped", False)
        # v_i is as it is in graph file
        if not mapped:
            mapped_v_i = self.get_vertex_index(v_i)
        # v_i is same as in the edges structure
        else:
            mapped_v_i = v_i
        if self.structure == ADJ_LIST:
            return self.edges[mapped_v_i]
        else:
            neighbors = {}
            for v_j in xrange(self.n_vertices):
                # Some graphs may have 0 as a valid weight
                e_w = self.edges[mapped_v_i][v_j]
                if e_w != self.null_weight:
                    neighbors[v_j] = e_w
            return neighbors

    def get_vertex_index(self, v_i):
        """
        Returns mapped vertex index in graph structure

        Parameters
        ---------
        v_i: index label as it appears in the graph
        """
        # If it is a new vertex, add it to the map
        if v_i not in self.vertices_map:
            self.vertices_map[v_i] = self.__vertex_index
            self.indexes_map[self.__vertex_index] = v_i
            # Increasing index for next element
            self.__vertex_index += 1
        return self.vertices_map[v_i]


    def connected_components(self, method, *args, **kwargs):
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
        if self.structure == ADJ_LIST:
            for v_i, neighbors in self.edges.iteritems():
                degree = len(neighbors)
                avg_degree += degree
                update_degree_pdf(degree_pdf, degree, self.n_vertices)
        #
        if self.structure == ADJ_MATRIX:
            for v_i in xrange(self.n_vertices):
                degree_i = 0
                for v_j in xrange(self.n_vertices):
                    if self.edges[v_i, v_j] != self.null_edge_weight:
                        degree_i += 1
                avg_degree += degree_i
                update_degree_pdf(degree_pdf, degree_i, self.n_vertices)
        return degree_pdf, avg_degree/self.n_vertices

    def label_to_vertices(self, label_file_path):
        """
        Loads labels for vertices returns mapping
        
        Parameters
        ----------
        label_file_path: str
            Path for file with following pattern: v_i,label_to_v_i
        
        Returns:
        dict, dict
            First dictionary maps label to index, meanwhile the
            second dictionary second maps index to label
        """
        label_map = {}
        reverse_map = {}
        label_file = open(label_file_path,'r')
        for vertex_info in label_file:
            vertex_index, vertex_label = vertex_info.rstrip("\n").split(",")
            # Tries to convert to int, sometimes it is useful!
            try:
                vertex_index = int(vertex_index)
            except:
                vertex_index = vertex_index
            # We need to consider the file not covering the whole graph
            if vertex_index in self.vertices_map:
                label_map[vertex_label] = vertex_index
                reverse_map[vertex_index] = vertex_label
            else:
                pass
        return label_map, reverse_map

    def labeled_vertices(self, reverse_map, vertices_list):
        """
        Translates list of vertices to its respective label mapping
        
        Parameters
        ----------
        reverse_map: dict
            Mapping from vertex index to its label
        vertices_list: list
            Vertices to translate

        Returns
        -------
        list
            List of labeled vertices
        """
        labeled_vertices = []
        for vertex in vertices_list:
            labeled_vertices.append(reverse_map[vertex])
        return labeled_vertices
    
    def export_graph_info(self, *args, **kwargs):
        """
        Generates file with graph information, such as degree distribution
        and number of vertices, edges and the average degree
        """
        degree_distribution, avg_degree = self.degree_distribution()
        info_file = open("INFO_"+self.input_file_path, "w+")
        info_file.write("# n = "+str(self.vertices_count)+"\n")
        info_file.write("# m = "+str(self.edges_count)+"\n")
        info_file.write("# d_medio = "+str(avg_degree)+"\n")
        for degree, frequency in degree_distribution.iteritems():
            info_file.write("%d %f\n" % (degree, frequency))
        info_file.close()
