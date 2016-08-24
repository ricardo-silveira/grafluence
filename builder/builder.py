"""
"""
import os
import csv
from subprocess import call


class Builder(object):
    """
    """
    def _make_graph(self, edges, output_path, **kwargs):
        """
        Exports graph file in csv format
        """
        header = kwargs.get("header", None)
        open_mode = kwargs.get("open_mode", "wb")
        with open(output_path, open_mode) as graph_file:
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

    def unify_edges(graph_path):
        """
        """
        temp_graph = "%.temp" % graph_path
        # sorting graph file
        call('(head -n 1 %(file)s && tail -n +2 %(file)s | sort) > %(file)s' % {"file": graph_path})
        with open(temp_graph, "wb") as temp_graph:
            temp_writer = csv.writer(temp_graph, delimiter=",")
            with open(graph_path, "r") as graph:
                first_line = True
                second_line = True
                graph_reader = csv.reader(graph, delimiter=",")
                for row in graph_reader:
                    if first_line:
                        temp_writer.writerow(row)
                        first_line = False
                    # Saving first edge and its weight
                    if second_line:
                        v_i, v_j, e_w = row
                        second_line = False
                    # Check in rest of file if the same edge happens
                    else:
                        n_v_i, n_v_j, n_e_w = row
                        # if same edge, add its weight
                        if n_v_1 == v_i and n_v_j == v_j:
                            e_w += n_e_w
                        # When finding new edge, write previous on file
                        else:
                            temp_writer.writerow([v_i, v_j, n_e_w])
                            v_i, v_j, e_w = n_v_i, n_v_j, n_e_w
        call("mv %s %s" % (temp_graph, graph_path))
