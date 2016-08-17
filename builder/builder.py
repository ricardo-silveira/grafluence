"""
"""
import os
import csv

class Builder(object):
    """
    """
    def _make_graph(self, edges, output_path, **kwargs):
        """
        Exports graph file in csv format
        """
        header = kwargs.get("header", None)
        with open(output_path, "wb") as graph_file:
            writer = csv.writer(graph_file)
            if header:
                writer.writerow(header)
            for v_i, neighbors in edges.iteritems():
                for v_j, weight in neighbors.iteritems():
                    writer.writerow([v_i, v_j, weight])

    def add_edge(self, graph, v_i, v_j, weight, **kwargs):
        directed = kwargs.get("directed", False)
        if not directed and v_j < v_i:
            aux = v_i
            v_i = v_j
            v_j = aux
        if v_i not in graph:
            graph[v_i] = {}
        if v_j not in graph[v_i]:
            graph[v_i][v_j] = 0.0
        graph[v_i][v_j] += weight

    def standard_dirs(self):
        """
        """
        export_path = kwargs.get("export_path", "data/")
        if not os.path.exists(export_path):
            os.makedirs(export_path)
