"""
Module for plotting data
"""

def export_bar_graph(labels, labels_values, graph_path):
    """
    Plotting bar graph method
    
    :param labels: X-axis labels for bar graph
    :param labels_values: Y-axis for bar graph
    :graph_path: System path to generate graph
    """
    pylab.bar(range(len(labels)), labels_values, align='center')
    pylab.xticks(range(len(labels)), labels, rotation='vertical')
    pylab.savefig(graph_path, bbox_inches='tight')
    pylab.close()
