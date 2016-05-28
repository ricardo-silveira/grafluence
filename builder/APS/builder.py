"""
Builder module to extract graph from APS files
"""
import json


class Builder(object):
    """
    Class to build APS graphs
    """
    ROOT_PATH = "../../data/APS"
    CITATION_CSV_PATH = "aps-dataset-citations-2013/" +
                        "aps-dataset-citations-2013.csv"
    COAUTHORSHIP_DIR_PATH = "aps-dataset-metadata-2013"

    def __init__(self):
        self.CITATION_CSV_PATH = "%s/%s" % (self.ROOT_PATH,
                                            self.CITATION_CSV_PATH)
        self.COAUTHORSHIP_DIR_PATH = "%s/%s" % (self.ROOT_PATH,
                                                self.COAUTHORSHIP_DIR_PATH)

    def build_path(self, vertex_label, dir_path=self.COAUTHORSHIP_DIR_PATH):
        """
        Creates path to vertex file
        """
        file_name = vertex_label.split("/")[1]
        vertex_path = "%s/" % dir_path
        for _ch in file_name:
            if _ch.isupper():
                vertex_path += _ch
        # Only first number becomes a dir
        vertex_path = "%s/%s" % (vertex_path,
                                 "/".join(file_name.split(".")[1:2]))
        vertex_path = "%s/%s.json" % (vertex_path, file_name)
        return vertex_path

    def get_vertices_path(self):
        """
        Returns dictionary of vertices and their respective json file,which
        contains information about each paper
        """
        vertices = {}
        with open(self.CITATION_CSV_PATH) as citation_edges:
            first_line = True
            for edges in citation_edges:
                if not first_line:
                    target, source = edges.rstrip("\n").split(",")
                    if source not in vertices:
                        vertices[source] = self.build_path(source)
                    if target not in vertices:
                        vertices[target] = self.build_path(target)
                first_line = False
        return vertices
