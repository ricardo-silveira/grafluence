"""
"""
import os

class Builder(object):
    """
    """
    def standard_dirs(self):
        """
        """
        export_path = kwargs.get("export_path", "data/")
        if not os.path.exists(export_path):
            os.makedirs(export_path)

    def graph_format(self):
        """
        """
        pass

    def store_date(self):
        """
        """
        pass

    def export_graph(self):
        """
        """
        pass
