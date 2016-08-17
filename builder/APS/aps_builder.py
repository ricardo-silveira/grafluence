"""
Builder module to extract graph from APS files
"""
import os
import json
from dateutil.parser import parse
if __name__ == "__main__":
    import sys
    sys.path.append("../")
    from _helper import dump, set_dir, LOGGER
    from builder import Builder
else:
    from builder._helper import dump, set_dir, LOGGER
    from builder.builder import Builder
# pylint: disable=line-too-long, too-many-locals


class APSBuilder(Builder):
    """
    Builds citation and coauthorship graph based on APS (American Physical
    Society) dataset. If two researchers have published together and their
    work cites N other works, then the connection between these two
    researchers will be represented in the coauthorship graph. Meanwhile in
    the citation graph, each researcher will be linked to the authors of
    the cited works.

    Attributes
    ----------
    ROOT_PATH: str
        Root path to access any possible and valid path for program.
    CITATION_CSV_NAME: str
        Name of csv file which presents the citations links.
    WORKS_DIR_NAME: str
        Name of parent directory hosting all works json files.
    AUTHORS_LIMIT: int
        Not considerng works with more authors than this limit.
    works: dict
        Maps works by id to their publication date, cited works and authors.
    authors: dict
        Maps authors names to their respective ids in graph file.
    output_dir_path: str
        Path for to export all built data.

    Methods
    -------
    load_works(**kwargs):
        Reads json files in sub-dirs from `WORKS_DIR_NAME`, feeding `works`
        with their respectie id, list of authors and publication date.
    load_citations(**kwargs):
        Reads csv file with citations links, updating `works` with list of
        cited works by each work.
    group_by_time(**kwargs):
        Group works by time, appending list of works for each time mark.
    make_coauthorship_graph(**kwargs):
        Exports an undirected weighted graph, each line representing an
        author working together with another author. The weight is inversely
        proportional to the number of co-authors.
    make_citations_graph(**kwargs):
        Exports a directed weighted graph, each line representing an author
        citing the work of another author. The weight is inversely
        proportional to the number of authors in the cited work.
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
        """
        # Limits of authors to consider in graph
        self.authors_limit = kwargs.get("authors_limit", self.AUTHORS_LIMIT)
        # Directory to house built data
        self.output_dir_path = kwargs.get("output_dir_path", "output")
        set_dir(self.output_dir_path)
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
        Loads all works in json files in the metadata folder and their
        respective sub-directories.
        """
        # Loading settings
        dump_works = kwargs.get("dump", False)
        works_dump_name = kwargs.get("works_dump_name", "aps_works")
        authors_dump_name = kwargs.get("authors_dump_name", "aps_authors")
        works_dump_path = "%s/%s.json" % (self.output_dir_path,
                                          works_dump_name)
        authors_dump_path = "%s/%s.json" % (self.output_dir_path,
                                            authors_dump_name)
        search_dir_path = kwargs.get("search_dir_path", self.works_dir_path)
        load_from_dump = kwargs.get("load_from_dump", False)
        # Loading work from a previous build
        if load_from_dump:
            with open(works_dump_path, "r") as works_dump:
                self.works = json.load(works_dump)
            with open(authors_dump_path, "r") as authors_dump:
                self.authors = json.load(authors_dump)
            return
        overview = {"Publishers": 0,
                    "Works": 0,
                    "Retrieved": 0}
        # List of publishers
        for dir_name in os.listdir(search_dir_path):
            dir_path = "%s/%s" % (self.works_dir_path, dir_name)
            overview["Publishers"] += 1
            LOGGER.info("dir # %d: %s", overview["Publishers"], dir_name)
            # List of editions
            for sub_dir_name in os.listdir(dir_path):
                sub_dir_path = "%s/%s" % (dir_path, sub_dir_name)
                LOGGER.info("sub-dir: %s", sub_dir_name)
                # List of works in this edition
                for file_name in os.listdir(sub_dir_path):
                    overview["Works"] += 1
                    file_path = "%s/%s" % (sub_dir_path, file_name)
                    try:
                        # Gets publication_date and author list for each work
                        work_id, work_info = self._get_work_info(file_path)
                        if work_info:
                            overview["Retrieved"] += 1
                            self.works[work_id] = work_info
                    # Happens if file has any structural problem
                    except ValueError:
                        LOGGER.debug("ValueError exception for %s", work_id)
        LOGGER.info("Overview: %s", str(overview))
        # Dumping loaded data
        if dump_works:
            dump(self.works, works_dump_path)
            dump(self.authors, authors_dump_path)
            dump(overview, "%s/%s.txt" % (self.output_dir_path,
                                          "aps_works_overview"))
            dump(self.ignored_works, "%s/%s.json" % (self.output_dir_path,
                                                     "aps_ignored_works"))

    def _get_work_info(self, file_path):
        """
        Returns publication_id and a dictionary with authors list, publication
        date and an empt list for cited_works. This method also updates the
        authors dict, which holds each author identifier.
        """
        work_info = {}
        file_data = json.load(open(file_path))
        authors_list = []
        # Listing authors of publications, handling possible Editorials
        try:
            work_authors = file_data["authors"]
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
                except TypeError:
                    LOGGER.error("Bug at file %s", file_path)
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
        Loads relation of cited works from csv file, in which each line represents
        a work citing another.
        """
        line_counter = 0
        citation_csv_path = kwargs.get("citation_csv_path", self.citation_csv_path)
        with open(citation_csv_path) as csv_file:
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

    def group_by_time(self, **kwargs):
        """
        Returns dictionary with time and list of works matching the time
        window.
        """
        grouped_works = {}
        time_resolution = kwargs.get("time_resolution", "year")
        for work_id, work_info in self.works.iteritems():
            publication_date = parse(work_info["publication_date"])
            if time_resolution == "year":
                work_date = str(publication_date.year)
            if time_resolution == "month":
                work_date = "%d/%d" % (publication_date.month,
                                       publication_date.year)
            if work_date not in grouped_works:
                grouped_works[work_date] = []
            grouped_works[work_date].append(work_id)
        return grouped_works

    def make_coauthorship_graph(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author publishing a work with another author.
        The edges are weighted, which is inversely proportional to the number
        of co-authors in the work.
        """
        resolution = kwargs.get("resolution", "year")
        created_files = []
        grouped_works = self.group_by_time(time_resolution=resolution)
        # Directory for coauthorship graphs
        coauthorship_graphs_dir = "%s/coautorship_graphs" % self.output_dir_path
        for work_date, works_list in grouped_works.iteritems():
            # Creating one folder per year
            if time_resolution == "month":
                set_dir("%s/%s" % (coauthorship_graphs_dir, work_date.split("/")[0])
            graph_file_name = "%s/aps_coauthorship_%s.csv" % (coauthorship_graphs_dir,
                                                              work_date)
            created_files.append(graph_file_name)
            LOGGER.info("Building coauthorship graph %s", work_date)
            edges = {}
            # Listing works in that time period
            for work_id in works_list:
                authors = self.works[work_id]["authors"]
                authors_count = len(authors)
                # Non-individual works
                if authors_count > 1:
                    weight = 1.0/(authors_count-1)
                    for i in xrange(authors_count):
                        # avoiding repeated edges
                        for j in xrange(authors_count-i-1):
                            self.add_edge(edges, authors[i], authors[j+i+1], weight)
                # If solo-work, then represent edge with null weight
                if authors_count == 1:
                    self.add_edge(edges, authors[0], authors[0], 0.0)
            self._make_graph(edges, graph_file_name, header=["author_i", "author_j", "weight"])
            LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % coauthorship_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))

    def make_citation_graph(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author citing another author. The edges are
        weighted, which is inversely proportional to the number of authors
        in the cited work.
        """
        missing_works = {}
        resolution = kwargs.get("resolution", "year")
        grouped_works = self.group_by_time(time_resolution=resolution)
        period = kwargs.get("period", grouped_works.keys())
        citation_graphs_dir = "%s/citation_graphs" % self.output_dir_path
        set_dir(citation_graph_dir)
        # For each time mark T
        for work_date in period:
            # Creating one folder per year
            if time_resolution == "month":
                set_dir("%s/%s" % (citation_graphs_dir, work_date.split("/")[0])
            # Retrieving list of works
            works_list = grouped_works[work_date]
            # Creates file to write graph
            graph_file_name = "%s/aps_citation_%s.txt" % (citation_graphs_dir,
                                                          work_date)
            graph_file = open(graph_file_name, "w+")
            created_files.append(graph_file_name)
            LOGGER.info("Building coauthorship graph %s", work_date)
            edges = {}
            # For each work i in time T
            for work_id in works_list:
                # Loading list of authors and list of cited works
                cited_works = self.works[work_id]["cited_works"]
                work_authors = self.works[work_id]["authors"]
                # For each work j cited by work i
                for cited_work in cited_works:
                    try:
                        # Loading list of authors in work j
                        cited_authors = self.works[cited_work]["authors"]
                        weight = 1.0/len(cited_authors)
                        # For each author x \in work i
                        for author_a in work_authors:
                            # For each author y \in work j
                            for author_b in cited_authors:
                                self.add_edge(edges, authors[i], authors[j+i+1], weight)
                    except KeyError:
                        if cited_work not in missing_works:
                            missing_works[cited_work] = []
                            missing_works[cited_work].append(cited_work)
            self._make_graph(edges, graph_file_name, header=["author_i", "author_j", "weight"])
            LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % citation_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))


if __name__ == "__main__":
    APS_BUILDER = APSBuilder()
    APS_BUILDER.load_works(dump=False, load_from_dump=True)
    APS_BUILDER.make_coauthorship_graph()
    #APS_BUILDER.load_citations()
    #YEARS_LEFT = [1989+i for i in range(2013-1989+1)]
    #APS_BUILDER.citation_graph(period=YEARS_LEFT)
