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
        Creates path to metadata-json file

        Parameters
        ----------
        vertex_label: str
            label for vertex/work in csv file
        dir_path: str
            root path to be built on

        Returns
        -------
        str
            Path for json file which contains information about work,
            such as the authors and publication date.
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

    def get_works_path(self):
        """
        Returns dictionary of vertices and their respective json file path,
        which contains information about each work

        Returns
        -------
        dict
            Mapping work name and its corresponding json file path.
        """
        works = {}
        with open(self.CITATION_CSV_PATH) as citation_edges:
            first_line = True
            for edges in citation_edges:
                if not first_line:
                    target, source = edges.rstrip("\n").split(",")
                    if source not in works:
                        works[source] = self.build_path(source)
                    if target not in works:
                        works[target] = self.build_path(target)
                first_line = False
        return works

    def get_work_info(self, work_path):
        """
        Returns relevant information from work.

        Parameters
        ---------
        work_path: str
            Path for json file which contains all information

        Returns
        -------
        dict
            Keys "authors", holding a list of authors names, and
            "publication_date".
        """
        authors = []
        publication_date = None
        work_data = json.loads(open(work_path))
        publication_date = work_data["date"]
        for author in work_date["authors"]:
            authors.append(author["name"])
        return {"authors": authors,
                "publication_date": publication_date}
