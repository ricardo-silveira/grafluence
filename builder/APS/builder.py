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

    def __init__(self, *args, **kwargs):
        self.CITATION_CSV_PATH = "%s/%s" % (self.ROOT_PATH,
                                            self.CITATION_CSV_PATH)
        self.COAUTHORSHIP_DIR_PATH = "%s/%s" % (self.ROOT_PATH,
                                                self.COAUTHORSHIP_DIR_PATH)
        self.CITATION_CSV_PATH = kwargs.get("citation_csv_path",
                                            self.CITATION_CSV_PATH)
        self.COAUTHORSHIP_DIR_PATH = kwargs.get("coauthorship_dir_path",
                                                self.COAUTHORSHIP_DIR_PATH)
        #self.works = {}
        #self.load_works(self.COAUTHORSHIP_DIR_PATH)

    def load_works(self, current_path, dir_list=None):
        """
        Finds json paths for all files in metadata folder
        """
        all_files_path = []

        for dir_name in listdir(current_path):
            dir_path = "%s/%s" % (current_path, dir_name)
            for sub_dir_name in listdir(dir_path):
                sub_dir_path = "%s/%s" % (dir_path, sub_dir_name)
                for file_name in listdir(sub_dir_path):
                    file_path = "%s/%s" % (sub_dir_path, file_name)
                    all_files_path.append(file_path)
                    work_id, work_info = self.get_info(file_path)
                    self.works[work_id] = work_info

    def get_info(self, file_path):
        """
        Returns publication_id and a dictionary with authors list and
        publication date

        Parameters
        ---------
        file_path: str
            Path for json file which contains all work information

        Returns
        -------
        (str, dict)
            publication_id, {"authors": list, "publication_date": date}
        """
        work_info = {}
        file_data = json.load(open(file_path))
        authors = []
        # Listing authors of publications, if there is any (Editorials)
        if "authors" in file_data:
            for author in file_data["authors"]:
                try:
                    authors.append(author["name"])
                except KeyError:
                    print author
                    print "==============================="
                    print file_path
        work_info["authors"] = authors
        work_info["publication_date"] = file_data["date"]
        work_info["cited_works"] = []
        work_id = file_data["id"]
        return work_id, work_info

    def load_citations(self):
        """
        """
        works = {}
        works_citations_json = open("APS_works_citations.json", "w+")
        with open(self.CITATION_CSV_PATH) as csv_file:
            first_line = True
            for line in csv_file:
                if not first_line:
                    target, source = line.rstrip("\n").split(",")
                    if source in works:
                        works[source].append(target)
                    else:
                        works[source] = [target]
                first_line = False
        works_citations_json.write(json.dumps(works))
        works_citations_json.close()

    def load_coauthorship(self):
        """
        """
        works_dates_json = open("APS_works_dates.json", "w+")
        authors_works_json = open("APS_authors_works.json", "w+")
        works_dates = {}
        authors_works = {}
        works_citations = {}
        # For each work u
        for work_id, work_info in self.works.iteritems():
            authors_list = work_info["authors"]
            cited_works_list = work_info["cited_works"]
            publication_date = work_info["publication_date"]
            works_dates[work_id] = publication_date
            for author in authors_list:
                if author not in authors_works:
                    authors_works[author] = []
                authors_works[author].append(work_id)
        works_dates_json.write(json.dumps(works_dates))
        authors_works_json.write(json.dumps(authors_works))
        works_dates_json.close()
        authors_works_json.close()

if __name__ == "__main__":
    aps_builder = Builder()
    #aps_builder.export_graphs()
    aps_builder.load_citations()
