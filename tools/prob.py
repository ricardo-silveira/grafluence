"""
"""

def ccdf(values_list):
    """
    Counter cumulative density function
    :param values_list: input data for ccdf
    :returns: dictionary with values as probability
    """
    hist = {}
    total = len(values_list)
    n_len = float(1)/total
    print ">> Adjusting list of values"
    values_list = map(int, values_list)
    values_list.sort()
    values_list.append(None)
    print ">> Computing distribution"
    previous_value = None
    value_count = 1
    list_index = 0
    for i in values_list:
        if i == previous_value:
            value_count += 1
        else:
            if previous_value is not None:
                hist[previous_value] = n_len*(value_count+(total-list_index))
                value_count = 1
            previous_value = i
        list_index += 1
    return hist

def get_distribution(values_list, distr_type='ccdf'):
    """
    :param values_list: list of numeric values
    :param distr_type: string to select distribution type
    """
    if distr_type == "ccdf":
        return ccdf(values_list)
