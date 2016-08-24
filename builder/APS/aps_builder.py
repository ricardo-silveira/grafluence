"""
Builder module to extract graph from APS files
"""
import os
import json
import time
from dateutil.parser import parse
if __name__ == "__main__":
    import sys
    sys.path.append("../")
from builder import Builder
from _helper import dump, set_dir, LOGGER
# pylint: disable=line-too-long


# CONSTS FOR ACCESSING LIST IN A READABLE WAY
WORK_INFO = 1
AUTHORS_LIST = 0
CITED_WORKS = 1
WORK_ID = 2


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
    find_works(**kwargs):
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

    def __init__(self, **kwargs):
        """
        Sets paths for input and output files, starts dictionary to hold
        works and authors and their respective identifiers.
        """
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
        # Each element has publication date, authors and cited works
        self.works = []
        # Mapping work id to is corresponding element index in works list
        self.works_map = {}
        # Number of elements in the the works list
        self.works_count = 0
        # Mapping author name to is corresponding element index in authors list
        self.authors_map = {}
        # Number of elements in the the authors list
        self.authors_count = 0

    def find_works(self, **kwargs):
        """
        Loads all works in json files in the metadata folder and their
        respective sub-directories.

        Parameters
        ----------
        search_dir_path: str
            Path for root directory to run a breadth search to find works.
        """
        overview = {"Publishers": 0,
                    "Works": 0,
                    "Retrieved": 0}
        search_dir_path = kwargs.get("search_dir_path", self.works_dir_path)
        LOGGER.info("Searching for works...")
        before = time.time()
        # List of publishers
        for dir_name in os.listdir(search_dir_path):
            dir_path = "%s/%s" % (self.works_dir_path, dir_name)
            overview["Publishers"] += 1
            LOGGER.debug("dir # %d: %s", overview["Publishers"], dir_name)
            # List of editions
            for sub_dir_name in os.listdir(dir_path):
                sub_dir_path = "%s/%s" % (dir_path, sub_dir_name)
                # List of works in this edition
                for file_name in os.listdir(sub_dir_path):
                    overview["Works"] += 1
                    file_path = "%s/%s" % (sub_dir_path, file_name)
                    # Gets publication_date and author list for each work
                    work_date, work_info = self._get_work_info(file_path)
                    if work_date:
                        overview["Retrieved"] += 1
                        self.works.append((work_date, work_info))
        # Exporting general info
        dump(overview, "%s/%s.txt" % (self.output_dir_path,
                                      "aps_works_overview"))
        LOGGER.info("Loaded %d works after %f seconds", overview["Retrieved"],
                                                        time.time() - before)
        self.sort_elements()

    def _get_work_info(self, file_path):
        """
        Returns publication_id and a dictionary with authors list, publication
        date and an empt list for cited_works. This method also updates the
        authors dict, which holds each author identifier.

        Parameters
        ----------
        file_path: str
            Path for json file with work information.

        Returns
        -------
        (str, [list, list, str])
            (work_date, [list of authors, list of cited works, work_id])
        """
        file_data = json.load(open(file_path))
        authors_list = []
        # Listing authors of publications, handling possible Editorials
        try:
            work_authors = file_data["authors"]
            for author in work_authors:
                # Handling error if author does not have a name in json
                try:
                    # Assigns an id for the author
                    if isinstance(author, dict) and author["name"] not in self.authors_map:
                        self.authors_map[author["name"]] = self.authors_count
                        self.authors_count += 1
                    author_idx = self.authors_map[author["name"]]
                    # Inserts author id in list of authors
                    authors_list.append(author_idx)
                except KeyError:
                    LOGGER.error("Work: %s, Bug: unnamed author %s", file_path, str(author))
                except TypeError, exc:
                    LOGGER.error("Work: %s, Bug: %s", file_path, exc)
                    return None, None
        except KeyError:
            LOGGER.error("Work: %s, Alert: 0 authors!", file_path)
            return None, None
        return (file_data["date"], [authors_list, [], file_data["id"]])

    def sort_elements(self):
        """
        """
        LOGGER.info("Sorting elements...")
        before = time.time()
        # Sorting works by date
        self.works.sort()
        # Mapping work_id and their respective index in list
        for work_idx, (work_date, work_info) in enumerate(self.works):
            work_id = work_info.pop(WORK_ID)
            self.works_map[work_id] = work_idx
        LOGGER.info("Elements sorted after %f seconds", time.time() - before)

    def load_from_dump(self, **kwargs):
        authors_dump_name = kwargs.get("authors_dump_name", "aps_authors")
        authors_dump_path = "%s/%s.json" % (self.output_dir_path,
                                            authors_dump_name)
        works_dump_name = kwargs.get("works_dump_name", "aps_works")
        works_dump_path = "%s/%s.json" % (self.output_dir_path,
                                          works_dump_name)
        works_map_dump_path = works_dump_path.replace(".json", "_map.json")
        with open(works_map_dump_path, "r") as works_map_dump:
            self.works_map = json.load(works_map_dump)
        with open(works_dump_path, "r") as works_dump:
            self.works = json.load(works_dump)

    def dump_data(self, **kwargs):
        works_dump_path = kwargs.get("works_dump_path",
                                     "%s/%s.json" % (self.output_dir_path, "aps_works"))
        authors_dump_path = kwargs.get("authors_dump_path",
                                       "%s/%s.json" % (self.output_dir_path, "aps_authors"))
        works_map_dump_path = works_dump_path.replace(".json", "_map.json")
        authors_map_dump_path = authors_dump_path.replace(".json", "_map.json")
        # Dumping loaded data
        dump(self.works, works_dump_path)
        dump(self.works_map, works_map_dump_path)
        dump(self.authors_map, authors_map_dump_path)

    def load_citations(self, **kwargs):
        """
        Loads relation of cited works from csv file, in which each line represents
        a work citing another.

        Parameters
        ----------
        citation_csv_path: str
            Path for csv file with works citations.
        """
        line_counter = 0
        citation_csv_path = kwargs.get("citation_csv_path", self.citation_csv_path)
        not_listed = {}
        LOGGER.info("Loading citations!")
        before = time.time()
        with open(citation_csv_path) as csv_file:
            first_line = True
            for line in csv_file:
                line_counter += 1
                if line_counter % 50000 == 0:
                    LOGGER.debug("Line # %d", line_counter)
                # Avoids first line comment
                if not first_line:
                    source_id, target_id = line.rstrip("\n").split(",")
                    # ensuring source and target are known works
                    if source_id in self.works_map and target_id in self.works_map:
                        source = self.works_map[source_id]
                        target = self.works_map[target_id]
                        self.works[source][CITED_WORKS].append(target)
                    else:
                        if source_id not in not_listed:
                            not_listed[source_id] = 0
                        not_listed[source_id] += 1
                first_line = False
        dump(not_listed, "%s/%s.json" % (self.output_dir_path, "non_listed"))
        LOGGER.info("Non-listed works: %d", len(not_listed.keys()))
        LOGGER.info("%d citations loaded after %f seconds", line_counter, time.time() - before)

    @staticmethod
    def is_same_resolution(ref_date, check_date, resolution):
        """
        Returns True if check date belongs to same ref_date period.

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

    def group_by_time(self, **kwargs):
        """
        Considering that works list is already sorted by date.
        """
        groups = []
        # Becomes zero at first iteration
        time_index = -1
        resolution = kwargs.get("resolution", "year")
        # Used to compare dates
        first_date = True
        for work_idx, (work_date, work_info) in enumerate(self.works):
            work_date = parse(work_date)
            if first_date:
                group_date = work_date
                first_date = False
                groups.append([group_date, []])
                time_index += 1
            if not self.is_same_resolution(group_date, work_date, resolution):
                time_index += 1
                group_date = work_date
                groups.append([group_date, []])
            groups[time_index][1].append(work_idx)
        return groups

    def make_coauthorship_graphs(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author publishing a work with another author.
        The edges are weighted, which is inversely proportional to the number
        of co-authors in the work.
        """
        resolution = kwargs.get("resolution", "month")
        created_files = []
        grouped_works = self.group_by_time(resolution=resolution)
        # Directory for coauthorship graphs
        coauthorship_graphs_dir = "%s/coauthorship_graphs" % self.output_dir_path
        for (ref_date, works_list) in grouped_works:
            graph_file_name = self.get_graph_file_name(coauthorship_graphs_dir, ref_date, resolution, "coauthorship")
            created_files.append(graph_file_name)
            self._make_graph({}, graph_file_name, header=["author_i", "author_j", "weight"])
            LOGGER.info("Building coauthorship graph %s", ref_date)
            # Listing works in that time period
            for work_id in works_list:
                authors_list = self.works[work_id][WORK_INFO][AUTHORS_LIST]
                authors_count = len(authors_list)
                # Non-individual works
                if authors_count > 1:
                    weight = 1.0/(authors_count-1)
                    for i in xrange(authors_count):
                        edges = {}
                        author_i = authors_list[i]
                        # Avoids repeated edge in same click
                        for j in xrange(authors_count-1-i):
                            author_j = authors_list[j+i+1]
                            self.add_edge(edges, author_i, author_j, weight)
                        # Writes to file after each author
                        self._make_graph(edges, graph_file_name, open_mode="a")
                # If solo-work, then represent edge with null weight
                if authors_count == 1:
                    edges = {}
                    self.add_edge(edges, authors_list[0], authors_list[0], 0.0)
                    self._make_graph(edges, graph_file_name, open_mode="a")
            self.unify_edges(graph_file_name)
            LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % coauthorship_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))

    def get_graph_file_name(self, output_dir, ref_date, resolution, g_type):
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

    def make_citation_graphs(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author citing another author. The edges are
        weighted, which is inversely proportional to the number of authors
        in the cited work.
        """
        resolution = kwargs.get("resolution", "year")
        grouped_works = self.group_by_time(resolution=resolution)
        citation_graphs_dir = "%s/citation_graphs" % self.output_dir_path
        set_dir(citation_graphs_dir)
        created_files = []
        # For each time mark T
        for (ref_date, works_list) in grouped_works:
            LOGGER.info("Building citation graph %s", ref_date)
            graph_file_name = self.get_graph_file_name(citation_graphs_dir, ref_date, resolution, "citations")
            created_files.append(graph_file_name)
            self._make_graph({}, graph_file_name, header=["author_i", "author_j", "weight"])
            # For each work i in time T
            for work_id in works_list:
                # Loading list of authors and list of cited works
                cited_works = self.works[work_id]["cited_works"]
                work_authors = self.works[work_id]["authors"]
                # For each work j cited by work i
                edges = {}
                for cited_work in cited_works:
                    try:
                        # Loading list of authors in work j
                        cited_authors = self.works[cited_work]["authors"]
                        weight = 1.0/len(cited_authors)
                        # For each author x \in work i
                        for author_a in work_authors:
                            # For each author y \in work j
                            for author_b in cited_authors:
                                self.add_edge(edges, author_a, author_b, weight, directed=True)
                    except KeyError:
                        pass
                self._make_graph(edges, graph_file_name, open_mode="a+")
            self.unify_edges(graph_file_name)
            LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % citation_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))


if __name__ == "__main__":
    APS_BUILDER = APSBuilder()
    #APS_BUILDER.find_works()
    #APS_BUILDER.load_citations()
    #APS_BUILDER.dump_data()
    #APS_BUILDER.load_from_dump()
    #APS_BUILDER.make_coauthorship_graphs(resolution="month")
    #APS_BUILDER.make_citation_graphs(resolution="month")
