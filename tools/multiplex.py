"""
Multiplex network structure
"""
from graph import Graph


# from dateutil import parser
# parser.parse(date_a)
# parser.parse(date_b)
# diff = (date_b - date_a).days


class Multiplex(object):
    """
    Multiplex class
    """
    def __init__(self, *args, **kwargs):
        """
        Arguments
        ----------
        list of graphs to be loaded

        Keyword Arguments
        -----------------
        """
        self.graphs_list = []
        for g_i in args:
            if isinstance(g_i, Graph):
                self.graphs_list.append(g_i)

    # We use three directed graphs
    # Graph A (directed) connects works and their respective publication dates
    # Graph B (undirected) connects authors to their respective works
    # Graph C (directed) connects works and their cited works
    # But in reality we want virtual graphs that uses these graphs
    # as information base
    # VirtualGraph A:
    # -> Connects authors that worked together (coauthorship)
    # -> get_neighbors: given a vertex, go to Graph B, find author, select 
    # list of works, for each work, go on Graph A and select its date, then go
    # to each work and list the authors and return the authors 
    # VirtualGraph B:
    # -> Connects authors that cited others (citation)
    # -> get_neighbors: given a vertex, select list of works, then for each
    # go in graph C, select list of works, then get back on graph B to find
    # its authors
