import json
import heapq
import contextlib2


def avoid_first_line(file_iterator):
    first_line = True
    for line in file_iterator:
        if not first_line:
            yield line
        first_line = False

citation_path = "../data/APS/output/graph/citation_graphs/files.json"
#coauthorship_path = "../data/APS/output/graph/coauthorship_graphs/files.json"

all_files_citation = [x.replace("output/", "output/graph/") for x in json.load(open(citation_path))]
#all_files_coauthorship = [x.replace("output/", "output/graph/") for x in json.load(open(coauthorship_path))]

def external_merge(files_path):
    filenames_year = {}
    root_path = "../data/APS"
    for file_path in files_path:
        # selecting files for year
        info = file_path.split("/")
        year = info[3]
        graph_path = "%s/%s" % (root_path, "/".join(info[:-1])+"/%s.txt" % year)
        file_path = "%s/%s" % (root_path, file_path)
        if graph_path not in filenames_year:
            filenames_year[graph_path] = []
        filenames_year[graph_path].append(file_path)
    for graph_path, filenames in filenames_year.iteritems():
        # merging files for each year
        print graph_path
        with contextlib2.ExitStack() as stack:
            files = [avoid_first_line(stack.enter_context(open(fn))) for fn in filenames]
            with open(graph_path, "w") as f:
                f.writelines(heapq.merge(*files))

#external_merge(all_files_coauthorship)
external_merge(all_files_citation)
