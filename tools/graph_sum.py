"""
Joins graphs in one
"""
import json


files_path = json.load(open("all_files.json"))

def count_graph(adj_list):
    vertices_count = 0
    edges_count = 0
    for vertice, neighbors in adj_list.iteritems():
        vertices_count += 1
        edges_count += len(neighbors.keys())
    return (vertices_count, edges_count)

data = []
adj_list = {}
for graph_file_path in files_path:
    first_line = True
    with open(graph_file_path) as graph_file:
        for line in graph_file:
            if not first_line:
                v_i, v_j, e_w = line.split(",")
                if v_i not in adj_list:
                    adj_list[v_i] = {}
                adj_list[v_i][v_j] = e_w
        data.append(count_graph(adj_list))

with open("graph_cum.json", "w+") as graph_cum_file:
    json.dump(data, graph_cum_file)

with open("total_graph.json", "w+") as total_graph:
    json.dump(adj_list, total_graph)
