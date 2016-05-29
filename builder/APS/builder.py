"""
Builder module to extract graph from APS files
"""
import json
from os import listdir
from os.path import isfile, join


class Builder(object):
    """
    Class to build APS graphs
    """
    ROOT_PATH = "../../data/APS"
    CITATION_CSV_PATH = "aps-dataset-citations-2013/"
    CITATION_CSV_PATH += "aps-dataset-citations-2013.csv"
    COAUTHORSHIP_DIR_PATH = "aps-dataset-metadata-2013"

    def __init__(self):
        self.CITATION_CSV_PATH = "%s/%s" % (self.ROOT_PATH,
                                            self.CITATION_CSV_PATH)
        self.COAUTHORSHIP_DIR_PATH = "%s/%s" % (self.ROOT_PATH,
                                                self.COAUTHORSHIP_DIR_PATH)
        self.works = {}
        self.load_works(self.COAUTHORSHIP_DIR_PATH)

    def load_works(self, current_path, dir_list=None):
        """
        Recursively finds json paths for all files in metadata folder
        """
        if isfile(current_path):
            work_id, work_info = self.get_info(current_path)
            self.works[work_id] = work_info
        else:
            for this_path in listdir(current_path):
                self.load_works("%s/%s" % (current_path, this_path))

    def get_info(self, file_path):
        """
        Returns authors, publication date and id.

        Parameters
        ---------
        file_path: str
            Path for json file which contains all work information
        """
        work_info = {}
        file_data = json.load(open(file_path))
        authors = []
        # 
        if "authors" in file_data:
            for author in file_data["authors"]:
                authors.append(author["name"])
        work_info["authors"] = authors
        # 
        work_date = ""
        if "date" in file_data:
            work_date = file_data["date"]
        work_info["publication_date"] = work_date
        #
        work_id = file_data["id"]
        return work_id, work_info
