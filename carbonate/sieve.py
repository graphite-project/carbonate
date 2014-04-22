def filterMetrics(inputs, node, cluster, invert=False, filter_long=False):
    if isinstance(node, basestring):
        match = [node]
    else:
        match = node

    if filter_long:
        dest_mapper = lambda m: ':'.join(map(str, m))
    else:
        dest_mapper = lambda m: m[0]

    for metric_name in inputs:
        dests = map(dest_mapper, cluster.getDestinations(metric_name))
        if set(dests) & set(match):
            if not invert:
                yield metric_name
        else:
            if invert:
                yield metric_name
