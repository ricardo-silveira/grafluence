import json

DEGREE = 0
WEIGHT = 1
ROOT_PATH = "../builder/APS/"

def update_weight(vertices, v_i, e_w):
    if v_i not in vertices:
        vertices[v_i] = [0, 0.]
    vertices[v_i][WEIGHT] += e_w

def update_degree(vertices, v_i):
    if v_i not in vertices:
        vertices[v_i] = [0, 0.]
    vertices[v_i][DEGREE] += 1

def get_static_info(graph_file_path):
    vertices = {}
    edges_count = 0
    with open(graph_file_path) as graph:
        first_line = True
        for edge in graph:
            if not first_line: 
                v_i, v_j, e_w = edge.rstrip("\r\n").split(",")
                edges_count += 1
                e_w = float(e_w)
                v_i = int(v_i)
                v_j = int(v_j)
                # different authors worked with
                update_degree(vertices, v_i)
                update_degree(vertices, v_j)
                # useful to count works made by author
                update_weight(vertices, v_i, e_w)
                update_weight(vertices, v_j, e_w)
            if first_line:
                first_line = False
    vertices_count = len(vertices.keys())
    return vertices, vertices_count, edges_count

def get_avg_degree(vertices_count, edges_count):
    return float(edges_count)/(2*vertices_count)

def load_all_graphs(files_path):
    files_path_list = json.load(open(files_path))
    for file_path in files_path_list:
        vertices, n_vertices, m_edges = get_static_info(ROOT_PATH+file_path)
        output_path = file_path.replace(".json", "_VERTICES_INFO.json")
        output_file = open(ROOT_PATH+output_path, "w+")
        output_file.write(json.dumps(vertices))
        output_file.close()

if __name__ == "__main__":
    citation_dir = ROOT_PATH+"output/citation_graphs/files.json"
    coauthorship_dir = ROOT_PATH+"output/coauthorship_graphs/files.json"
    #load_all_graphs(coauthorship_dir)
    load_all_graphs(citation_dir)
