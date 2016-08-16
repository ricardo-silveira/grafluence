"""
Builder module to extract graph from APS files
"""
import json
import os
import logging
import glob
from dateutil.parser import parse


# pylint: disable=line-too-long, too-many-locals


# Log settings
LOGGER = logging.getLogger(__name__)
FMT = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
LOG_VERSION = len(glob.glob("build_*.log"))
FH = logging.FileHandler("build_%d.log" % LOG_VERSION)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
FH.setFormatter(FMT)
CH.setFormatter(FMT)
LOGGER.addHandler(FH)
LOGGER.addHandler(CH)
LOGGER.setLevel(logging.DEBUG)


class APSBuilder(object):
    """
    Class to build APS graphs
    """
    # pylint: disable=too-many-instance-attributes

    ROOT_PATH = "../../data/APS"
    CITATION_CSV_NAME = "aps-dataset-citations-2013.csv"
    WORKS_DIR_NAME = "aps-dataset-metadata-2013"
    AUTHORS_LIMIT = 100

    def __init__(self, **kwargs):
        """
        Sets paths for input and output files, starts dictionary to hold
        works and authors and their respective identifiers.

        Methods
        -------
        load_works
        get_work_info

        Parameters
        ----------
        root_path: str
        export_path: str
        citation_csv_path: str
        coauthorship_dir_path: str
        """
        # Limits of authors to consider in graph
        self.authors_limit = kwargs.get("authors_limit", self.AUTHORS_LIMIT)
        # Directory to house built data
        self.output_dir_path = kwargs.get("output_dir_path", "output/")
        if not os.path.exists(self.output_dir_path):
            os.makedirs(self.output_dir_path)
        # Setting default paths
        self.root_path = kwargs.get("root_path", self.ROOT_PATH)
        self.citation_csv_path = "%s/%s/%s" % (self.root_path,
                                               "aps-dataset-citations-2013",
                                               self.CITATION_CSV_NAME)
        self.works_dir_path = "%s/%s" % (self.root_path,
                                         self.WORKS_DIR_NAME)
        # Changing paths if specified
        self.citation_csv_path = kwargs.get("citation_csv_path",
                                            self.citation_csv_path)
        self.works_dir_path = kwargs.get("works_dir_path",
                                         self.works_dir_path)
        self.works = {}
        self.authors = {}
        self.authors_count = 0
        self.ignored_works = []

    def load_works(self, **kwargs):
        """
        Finds json paths for all files in metadata folder.

        Parameters
        ----------
        search_dir_path: str
            root path to start searching for works, considering they are listed
            in subfolder for publisher name and another subfolder for the
            edition of publication.
        works_dump_name: str
        authors_dump_name: str
        dump: bool
            if True, dumps works and authors to file.
        """
        dump = kwargs.get("dump", False)
        works_dump_name = kwargs.get("works_dump_name", "aps_works")
        authors_dump_name = kwargs.get("authors_dump_name", "aps_authors")
        works_dump_path = "%s/%s.json" % (self.output_dir_path,
                                          works_dump_name)
        authors_dump_path = "%s/%s.json" % (self.output_dir_path,
                                            authors_dump_name)
        search_dir_path = kwargs.get("search_dir_path", self.works_dir_path)
        load_from_dump = kwargs.get("load_from_dump", False)
        if load_from_dump:
            with open(works_dump_path, "r") as works_dump:
                self.works = json.load(works_dump)
            with open(authors_dump_path, "r") as authors_dump:
                self.authors = json.load(authors_dump)
            return
        dir_count = 0
        work_count = 0
        retrieved_count = 0
        # List of publishers
        for dir_name in os.listdir(search_dir_path):
            dir_path = "%s/%s" % (self.works_dir_path, dir_name)
            dir_count += 1
            LOGGER.info("dir # %d: %s", dir_count, dir_name)
            # List of editions
            for sub_dir_name in os.listdir(dir_path):
                sub_dir_path = "%s/%s" % (dir_path, sub_dir_name)
                LOGGER.info("sub-dir: %s", sub_dir_name)
                # List of works in this edition
                for file_name in os.listdir(sub_dir_path):
                    work_count += 1
                    file_path = "%s/%s" % (sub_dir_path, file_name)
                    try:
                        # Gets publication_date and author list for each work
                        work_id, work_info = self.get_work_info(file_path)
                        if work_info:
                            retrieved_count += 1
                            self.works[work_id] = work_info
                    # Not exactly sure why it happened once...
                    except ValueError:
                        LOGGER.debug("ValueError exception for %s", work_id)
        LOGGER.info("Total works: %d", work_count)
        LOGGER.info("Works retrieved: %d", retrieved_count)
        if dump:
            works_dump = open(works_dump_path, "w+")
            works_dump.write(json.dumps(self.works))
            works_dump.close()
            LOGGER.info("Output file at %s", works_dump_path)
            # More readable
            authors_dump = open(authors_dump_path, "w+")
            authors_dump.write(json.dumps(self.authors))
            authors_dump.close()
            LOGGER.info("Output file at %s", authors_dump_path)
        works_info_path = "%s/%s.txt" % (self.output_dir_path, "aps_works_info")
        with open("%s/aps_works_info.txt" % self.output_dir_path, "w+") as works_info:
            works_info.write("Publishers: %d\n" % dir_count)
            works_info.write("Works: %d\n" % work_count)
            works_info.write("Editorials: %d\n" % (work_count-retrieved_count))
        ignored_works_path = "%s/%s.json" % (self.output_dir_path, "aps_ignored_works")
        with open("%s/aps_ignored_works.json" % self.output_dir_path, "w+") as ignored_works:
            ignored_works.write(json.dumps(self.ignored_works))

    def get_work_info(self, file_path):
        """
        Returns publication_id and a dictionary with authors list, publication
        date and an empt list for cited_works. This method also updates the
        authors dict, which holds each author identifier.

        Parameters
        ----------
        file_path: str
            Path for json file which contains all work information

        Returns
        -------
        (str, dict)
            publication_id, {"authors": list,
                             "publication_date": date,
                             "cited_works": list}
        """
        work_info = {}
        file_data = json.load(open(file_path))
        authors_list = []
        # Listing authors of publications, handling possible Editorials
        try:
            work_authors = file_data["authors"]
            # Avoiding giant works
            if len(file_data["authors"]) > self.AUTHORS_LIMIT:
                LOGGER.debug("%s: Authors limit exceeded: %d", file_path,
                                                               len(work_authors))
                self.ignored_works.append({"path": file_path,
                                           "authors_count": len(work_authors)})
                return None, None
            for author in work_authors:
                # Handling error if author does not have a name in json
                try:
                    # Assigns an id for the author
                    if isinstance(author, dict) and author["name"] not in self.authors:
                        self.authors[author["name"]] = self.authors_count
                        self.authors_count += 1
                    # Inserts author id in list of authors
                    authors_list.append(self.authors[author["name"]])
                except KeyError:
                    LOGGER.debug("Author %s with no name at %s", str(author), file_path)
                except TypeError, exp:
                    LOGGER.error("Bug at file %s", file_path)
                    pass
        except KeyError:
            LOGGER.debug("Work %s has 0 authors", file_path)
            self.ignored_works.append({"path": file_path,
                                       "authors_count": 0})
            return None, None
        work_info["authors"] = authors_list
        work_info["publication_date"] = file_data["date"]
        work_info["cited_works"] = []
        work_id = file_data["id"]
        return work_id, work_info

    def load_citations(self, **kwargs):
        """
        Loads relation of cited works.
        """
        line_counter = 0
        # dump = kwargs.get("dump", False)
        # citations_dump_name = kwargs.get("citations_dump_name", "aps_citations")
        with open(self.citation_csv_path) as csv_file:
            first_line = True
            LOGGER.info("Loading citations!")
            for line in csv_file:
                line_counter += 1
                if line_counter % 1000 == 0:
                    LOGGER.info("Line # %d", line_counter)
                # Avoids first line comment
                if not first_line:
                    source, target = line.rstrip("\n").split(",")
                    # ensuring source is a known work
                    if source in self.works:
                        self.works[source]["cited_works"].append(target)
                    else:
                        LOGGER.debug("Not listed: %s", source)
                first_line = False
        # citations_dump_path = "%s/%s.json" % (self.output_dir_path,
        #                                       citations_dump_name)

    def group_by_time(self, **kwargs):
        """
        Returns dictionary with time and list of works matching the time
        window.

        Parameters
        ----------
        time_resolution: str
            expected: 'year' or 'month'

        Returns
        -------
        dict:
            time marker and list of works published in that period.
        """
        grouped_works = {}
        time_resolution = kwargs.get("time_resolution", "year")
        for work_id, work_info in self.works.iteritems():
            publication_date = parse(work_info["publication_date"])
            if time_resolution == "year":
                work_date = publication_date.year
            if time_resolution == "month":
                work_date = publication_date.month
            if work_date not in grouped_works:
                grouped_works[work_date] = []
            grouped_works[work_date].append(work_id)
        return grouped_works

    def coauthorship_graph(self):
        """
        Generates several graph files for coauthorhips
        """
        grouped_works = self.group_by_time(time_resolution="year")
        for work_date, works_list in grouped_works.iteritems():
            # Directory for coauthorship graphs
            coauthorship_graphs_dir = "%s/coautorship_graphs" % self.output_dir_path
            if not os.path.exists(coauthorship_graphs_dir):
                os.makedirs(coauthorship_graphs_dir)
            # One graph file per time period
            graph_file_name = "%s/aps_coauthorship_%s.txt" % (coauthorship_graphs_dir,
                                                              work_date)
            graph_file = open(graph_file_name, "w+")
            graph_str = ""
            # Listing works in that time period
            for work_id in works_list:
                authors = self.works[work_id]["authors"]
                # No solo-works (therefore no-coauthorship)
                if len(authors) > 1:
                    weight = 1.0/(len(authors)-1)
                    # Click with N vertices
                    for author_a in authors:
                        for author_b in authors:
                            if author_a != author_b:
                                graph_str += "%d;%d;%f\n" % (author_a,
                                                             author_b,
                                                             weight)
            graph_file.write(graph_str)
            graph_file.close()

    def citation_graph(self, **kwargs):
        """
        Generates several graph files for citations
        """
        missing_works = {}
        grouped_works = self.group_by_time(time_resolution="year")
        period = kwargs.get("period", grouped_works.keys())
        for work_date in period:
            works_list = grouped_works[work_date]
            citation_graphs_dir = "%s/citation_graphs" % self.output_dir_path
            if not os.path.exists(citation_graphs_dir):
                os.makedirs(citation_graphs_dir)
            graph_file_name = "%s/aps_citation_%s.txt" % (citation_graphs_dir,
                                                          work_date)
            graph_file = open(graph_file_name, "w+")
            graph_str = ""
            for work_id in works_list:
                cited_works = self.works[work_id]["cited_works"]
                work_authors = self.works[work_id]["authors"]
                for cited_work in cited_works:
                    try:
                        cited_authors = self.works[cited_work]["authors"]
                        weight = 1.0/len(cited_authors)
                        for author_a in work_authors:
                            for author_b in cited_authors:
                                graph_str = "%s\n%s;%s;%f" % (graph_str,
                                                              author_a,
                                                              author_b,
                                                              weight)
                    except KeyError:
                        if cited_work not in missing_works:
                            missing_works[cited_work] = []
                            missing_works[cited_work].append(cited_work)
            graph_file.write(graph_str)
            graph_file.close()
        with open("%s/aps_citation_missing_works.json") as missing_works:
            missing_works.write(json.dumps(missing_works))


if __name__ == "__main__":
    APS_BUILDER = Builder()
    APS_BUILDER.load_works(dump=False, load_from_dump=True)
    # APS_BUILDER.coauthorship_graph()
    # APS_BUILDER.load_citations()
    # YEARS_LEFT = [1989+i for i in range(2013-1989+1)]
    # APS_BUILDER.citation_graph(period=YEARS_LEFT)
