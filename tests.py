def build_path(vertex_label, dir_path):
    """
    Creates path to vertex file
    """
    file_name = vertex_label.split("/")[1]
    vertex_path = "%s/" % dir_path
    for _ch in file_name:
        if _ch.isupper():
            vertex_path += _ch
    vertex_path = "%s/%s" % (vertex_path, "/".join(file_name.split(".")[1:2]))
    vertex_path = "%s/%s.json" % (vertex_path, file_name)
    return vertex_path

import unittest

class TestAPSBuilder(unittest.TestCase):

    def test_build_path(self):
        """
        Tests if path to APS vertices is built correctly
        """
        vertex_label = "10.1103/PhysRevB.25.1065"
        dir_path = "data/APS/aps-dataset-metadata-2013"
        expected_path = "%s/PRB/25/PhysRevB.25.1065.json" % dir_path
        self.assertEqual(expected_path, build_path(vertex_label, dir_path))

if __name__ == "__main__":
    unittest.main()
