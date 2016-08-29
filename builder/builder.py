"""
"""
import os
import csv
from dateutil.parser import parse
from subprocess import call
from _helper import set_dir, LOGGER


class Builder(object):
    """
    Methods
    -------
    _make_graph(edges, output_path)
    add_edge(edges, v_i, v_j, weight)
    is_same_resolution(ref_date, check_date)
    group_by_time(items)
    sum_edges(graph_file_path)
    """

    @staticmethod
    def _make_graph(edges, output_path, **kwargs):
        """
        Exports graph file in csv format

        Parameters
        ----------

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

    @staticmethod
    def add_edge(graph, v_i, v_j, weight=1, **kwargs):
        """
        Inserts edge (v_i, v_j) in graph and its respective weight.

        Parameters
        ----------
        edges: dict
        v_i: int
        v_j: int
        weight: float

        Returns
        -------
        bool:
            True if edge was inserted successfully, False otherwise.

        Examples
        --------
        >>> edges = {}
        >>> add_edge(edges, 0, 1, 0.5)
        >>> True

        >>> edges = []
        >>> add_edge(edges, 0, 1, 0.5)
        >>> False

        >>> edges = {}
        >>> add_edge(edges, 0, 1)
        >>> True
        >>> edges[0]
        >>> {1: 1}

        >>> edges = {}
        >>> add_edge(edges, 0, 1, 0.5)
        >>> True
        >>> edges[0]
        >>> {1: 0.5}
        """
        try:
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
            return True
        except Exception:
            return False

    @staticmethod
    def is_same_resolution(ref_date, check_date, resolution):
        """
        Returns True if check date belongs to same ref_date period.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> solve_date("2015-10-24", "2015-10-20", "month")
        True

        >>> solve_date("2015-11-24", "2015-10-24", "month")
        False

        >>> solve_date("2015-11-24", "2015-05-20", "year")
        True

        >>> solve_date("2014-10-16", "2012-11-30", "year")
        False
        """
        if resolution in ["year", "month"]:
            aux_date = check_date.replace(year=max(ref_date, check_date).year)
            if resolution == "month":
                aux_date = aux_date.replace(month=max(ref_date, check_date).month)
                aux_date = aux_date.replace(day=ref_date.day)
            if aux_date != ref_date:
                return False
            else:
                return True

    @staticmethod
    def get_graph_file_name(output_dir, ref_date, resolution, g_type):
        """
        
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> 
        """
        # Creating one folder per year
        date_str = "%d/%d/%d" % (ref_date.year, ref_date.month, ref_date.day)
        if resolution == "month":
            graph_dir = set_dir("%s/%s" % (output_dir, date_str.split("/")[0]))
            graph_file_name = "%s/aps_%s_%s_%s.csv" % (graph_dir,
                                                       g_type,
                                                       date_str.split("/")[0],
                                                       date_str.split("/")[1])
        if resolution == "year":
            graph_dir = set_dir(output_dir)
            graph_file_name = "%s/aps_%s_%s.csv" % (graph_dir,
                                                    g_type,
                                                    date_str.split("/")[1])
        return graph_file_name

    @staticmethod
    def group_by_time(items, **kwargs):
        """
        
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> 
        """
        groups = []
        # Becomes zero at first iteration
        time_index = -1
        resolution = kwargs.get("resolution", "year")
        # Used to compare dates
        first_date = True
        for item_idx, (item_date, item_info) in enumerate(items):
            item_date = parse(item_date)
            if first_date:
                group_date = item_date
                first_date = False
                groups.append([group_date, []])
                time_index += 1
            if not Builder.is_same_resolution(group_date, item_date, resolution):
                time_index += 1
                group_date = item_date
                groups.append([group_date, []])
            groups[time_index][1].append(item_idx)
        return groups

    @staticmethod
    def sum_edges(graph_path):
        """
        
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> 
        """
        # sorting graph file
        graph_file = open(graph_path, "r")
        temp_graph = graph_file.readlines()
        graph_file.close()
        total_edges = len(temp_graph)-1
        # graph with ony one edge, nothing to do here
        if total_edges == 1:
            return
        header = temp_graph.pop(0)
        header = header.rstrip("\r\n").split(",")
        temp_graph.sort()
        with open(graph_path, "wb") as graph:
            writer = csv.writer(graph, delimiter=",")
            writer.writerow(header)
            edges_count = 0
            for edge in temp_graph:
                # Saving first edge and its weight
                if edges_count == 0:
                    v_i, v_j, e_w = edge.rstrip("\r\n").split(",")
                    e_w = float(e_w)
                # Check in rest of file if the same edge happens
                if edges_count > 0:
                    n_v_i, n_v_j, n_e_w = edge.rstrip("\r\n").split(",")
                    n_e_w = float(n_e_w)
                    # if same edge, add its weight
                    if n_v_i == v_i and n_v_j == v_j:
                        e_w += n_e_w
                    # New edge found
                    else:
                        # write previous edge on file
                        writer.writerow([v_i, v_j, e_w])
                        # gets new edge to be compared
                        v_i, v_j, e_w = n_v_i, n_v_j, n_e_w
                    # if this edge is the last in the graph
                    if edges_count + 1 == total_edges:
                        writer.writerow([v_i, v_j, n_e_w])
                edges_count += 1
