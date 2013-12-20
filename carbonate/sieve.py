def filterMetrics(inputs, node, cluster, invert=False):
    if isinstance(node, basestring):
        match = [node]
    else:
        match = node

    for metric_name in inputs:
        dests = map(lambda m: m[0], cluster.getDestinations(metric_name))
        if set(dests) & set(match):
            if not invert:
                yield metric_name
        else:
            if invert:
                yield metric_name
