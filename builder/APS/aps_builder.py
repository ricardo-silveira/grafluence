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
    Builds citation and co-authorship graph based on APS (American Physical
    Society) dataset. For co-authorship, the vertices are authors and the edges
    are undirected and represented if they have published a work together.
    As for citation graph, if the published work cites other works, each author
    of the citing work will be linked by a directed edge to every author in
    the cited works.

    Attributes
    ----------
    root_path: str
        Root path to access any possible and valid path for program.
    citation_csv_name: str
        Name of csv file which presents the citations links.
    works_dir_name: str
        Name of parent directory hosting all works metadata json files.
    works: list
        List of works with their their publication date, cited works and authors.
    works_map: dict
        Maps works by id to their publication date, cited works and authors.
    output_dir_path: str
        Path to export all built data.

    Methods
    -------
    find_works(**kwargs):
        Parses all json files found in sub-dirs from `WORKS_DIR_NAME`, getting
        authors information and publication date of each work.
    load_citations(**kwargs):
        Reads csv file with citations links, updating `works` with list of
        cited works by each work.
    group_by_time(**kwargs):
        Group works by time, appending list of works for each time mark.
    make_coauthorship_graph(**kwargs):
        Exports an undirected weighted graph for time mark. For each graph
        file, the lines represent the edges between two authors who published
        a work together. The weight is inversely proportional to the number
        authors in the work.
    make_citations_graph(**kwargs):
        Exports a directed weighted graph for time mark. For each graph
        file, the lines represent the edges between two authors who cited
        each other in a work. The weight is inversely proportional to the number
        authors in the cited work.
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

    def find_works(self):
        """
        Loads all works in json files in the metadata folder and their
        respective sub-directories. The work information is stored in
        `self.works`.
        """
        overview = {"Publishers": 0,
                    "Works": 0,
                    "Retrieved": 0}
        LOGGER.info("Searching for works...")
        before = time.time()
        # List of publishers
        for dir_name in os.listdir(self.works_dir_path):
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
                    # If data is fine, hence work_date is not None
                    if work_date:
                        overview["Retrieved"] += 1
                        self.works.append((work_date, work_info))
        # Exporting overview info
        dump(overview, "%s/%s.txt" % (self.output_dir_path,
                                      "aps_works_overview"))
        LOGGER.info("Loaded %d works after %f seconds", overview["Retrieved"],
                                                        time.time() - before)
        self.sort_elements()
        self.authors_map = None

    def _get_work_info(self, file_path):
        """
        Returns publication_id and a dictionary with authors list, publication
        date and an empt list for cited_works. This method also updates the
        authors dict, which holds each author identifier.
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
        Sorting works list by publication date, and for each work, sorting
        the list of authors.
        """
        LOGGER.info("Sorting elements...")
        before = time.time()
        # Sorting works by date
        self.works.sort()
        # Mapping work_id and their respective index in list
        for work_idx in xrange(len(self.works)):
            work_id = self.works[work_idx][WORK_INFO].pop(WORK_ID)
            self.works_map[work_id] = work_idx
            self.works[work_id][WORK_INFO][AUTHORS_LIST].sort()
        LOGGER.info("Elements sorted after %f seconds", time.time() - before)

    def load_from_dump(self, **kwargs):
        """
        Loads authors map, works map and works list json files into memory.

        Parameters
        ----------
        authors_dump_name: str
            Default: aps_authors
        works_dump_name: str
            Default: aps_works
        """
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

    def dump_data(self):
        """
        Saves authors map, works map and works list as json files.
        """
        works_dump_path = "%s/%s.json" % (self.output_dir_path, "aps_works")
        authors_dump_path = "%s/%s.json" % (self.output_dir_path, "aps_authors")
        works_map_dump_path = works_dump_path.replace(".json", "_map.json")
        authors_map_dump_path = authors_dump_path.replace(".json", "_map.json")
        # Dumping loaded data
        dump(self.works, works_dump_path)
        dump(self.works_map, works_map_dump_path)
        dump(self.authors_map, authors_map_dump_path)

    def load_citations(self):
        """
        Loads relation of cited works from csv file, in which each line represents
        a work citing another.
        """
        line_counter = 0
        not_listed = {}
        LOGGER.info("Loading citations!")
        before = time.time()
        with open(self.citation_csv_path) as csv_file:
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
                        self.works[source][WORK_INFO][CITED_WORKS].append(target)
                    else:
                        if source_id not in not_listed:
                            not_listed[source_id] = 0
                        not_listed[source_id] += 1
                first_line = False
        dump(not_listed, "%s/%s.json" % (self.output_dir_path, "non_listed"))
        LOGGER.info("Non-listed works: %d", len(not_listed.keys()))
        LOGGER.info("%d citations loaded after %f seconds", line_counter, time.time() - before)

    def make_coauthorship_graphs(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author publishing a work with another author.
        The edges are weighted, which is inversely proportional to the number
        of co-authors in the work.

        Parameters
        ----------
        resolution: str
            If 'year', the time period is year, creating a graph file per year.
            If 'month', the time period is month, creating a folder for each
            year within files for each month with data.
            Default: 'year'.
        start_from_year: int
            For time range, considering works published from this year onward.
            Default: 0.
        until_year: float
            For time range, considering works published until this year.
            Default: inf.

        Returns
        -------
        dict:
            Dictionary with paths for all created files.
        """
        resolution = kwargs.get("resolution", "month")
        from_year = kwargs.get("from_year", 0)
        until_year = kwargs.get("until_year", float("inf"))
        created_files = []
        grouped_works = self.group_by_time(self.works, resolution=resolution)
        # Directory for coauthorship graphs
        coauthorship_graphs_dir = "%s/coauthorship_graphs" % self.output_dir_path
        for (ref_date, works_list) in grouped_works:
            if ref_date.year >= from_year and ref_date.year < until_year:
                graph_file_name = self.get_graph_file_name(coauthorship_graphs_dir,
                                                           ref_date, resolution,
                                                           "coauthorship")
                created_files.append(graph_file_name)
                self._make_graph({}, graph_file_name, header=["author_i", "author_j", "weight"])
                LOGGER.info("Building coauthorship graph %s", ref_date)
                # Listing works in that time period
                for work_id in works_list:
                    self.coauthors_graph(work_id, graph_file_name)
                self.sum_edges(graph_file_name)
                LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % coauthorship_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))
        return created_files

    def coauthors_graph(self, work_id, graph_file_name):
        """
        Saves coauthorship graph for specified work_id in graph file
        at graph_file_name.

        Parameters
        ----------
        work_id: int
            index in list of works
        graph_file_name: str
            name of graph file to append more edges
        """
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

    def make_citation_graphs(self, **kwargs):
        """
        For each time period, writes a file representing a graph in which
        each line represents an author citing another author. The edges are
        weighted, which is inversely proportional to the number of authors
        in the cited work.

        Parameters
        ----------
        resolution: str
            If 'year', the time period is year, creating a graph file per year.
            If 'month', the time period is month, creating a folder for each
            year within files for each month with data.
            Default: 'year'.
        from_year: int
            For time range, considering works published from this year onward.
            Default: 0.
        until_year: int
            For time range, considering works published until this year.
            Default: inf.

        Returns
        -------
        dict:
            Dictionary with paths for all created files.
        """
        resolution = kwargs.get("resolution", "year")
        from_year = kwargs.get("from_year", 0)
        until_year = kwargs.get("until_year", float("inf"))
        grouped_works = self.group_by_time(self.works, resolution=resolution)
        citation_graphs_dir = "%s/citation_graphs" % self.output_dir_path
        set_dir(citation_graphs_dir)
        created_files = []
        # For each time mark T
        for (ref_date, works_list) in grouped_works:
            if ref_date.year >= from_year and ref_date.year < until_year:
                LOGGER.info("Building citation graph %s", ref_date)
                graph_file_name = self.get_graph_file_name(citation_graphs_dir,
                                                           ref_date,
                                                           resolution,
                                                           "citations")
                self._make_graph({},
                                 graph_file_name,
                                 header=["author_i", "author_j", "weight"])
                # For each work i in time T
                for work_id in works_list:
                    self.citations_graph(work_id, graph_file_name)
                created_files.append(graph_file_name)
                self.sum_edges(graph_file_name)
                LOGGER.info("Graph stored at %s", graph_file_name)
        with open("%s/files.json" % citation_graphs_dir, "wb") as files:
            files.write(json.dumps(created_files))
        return created_files

    def citations_graph(self, work_id, graph_file_name):
        """
        Saves citation graph for specified work_id in graph file
        at graph_file_name.

        Parameters
        ----------
        work_id: int
            index in list of works
        graph_file_name: str
            name of graph file to append more edges
        """
        # Loading list of authors and list of cited works
        cited_works = self.works[work_id][WORK_INFO][CITED_WORKS]
        work_authors = self.works[work_id][WORK_INFO][AUTHORS_LIST]
        # For each work j cited by work i
        for cited_work in cited_works:
            edges = {}
            try:
                # Loading list of authors in work j
                cited_authors = self.works[cited_work][WORK_INFO][AUTHORS_LIST]
                weight = 1.0/len(cited_authors)
                # For each author x \in work i
                for author_a in work_authors:
                    # For each author y \in work j
                    for author_b in cited_authors:
                        self.add_edge(edges, author_a, author_b, weight, directed=True)
            except KeyError:
                pass
            self._make_graph(edges, graph_file_name, open_mode="a+")


if __name__ == "__main__":
    APS_BUILDER = APSBuilder()
    #APS_BUILDER.find_works()
    APS_BUILDER.load_from_dump()
    #APS_BUILDER.load_citations()
    #APS_BUILDER.dump_data()
    APS_BUILDER.make_citation_graphs(resolution="year", until_year=1930)
    APS_BUILDER.make_coauthorship_graphs(resolution="year", until_year=1930)
