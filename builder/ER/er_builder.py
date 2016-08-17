import random


class ERBuilder(object):

    def __init__(self, **kwargs):
        self.edges_count = kwargs.get("edges_count")
        self.vertices_count = kwargs.get("vertices_count")
        self.graph_age = kwargs.get("graph_age")
        self.nodes = range(self.vertices_count)
        self.edges = list()
        for i in xrange(self.vertices_count):
            self.edges.append(dict())

    def add_random_edge(self, time_t):
        i = random.choice(self.nodes)
        j = random.choice(self.nodes)
        if i != j and j not in self.edges[i]:
            self.edges[i][j] = time_t

    def randomize_graph(self):
        for time_t in xrange(self.graph_age):
            for edge_i in xrange(self.edges_count):
                self.add_random_edge(time_t)
