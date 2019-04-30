from functools import partial

map_long = partial(map, lambda m: ':'.join(map(str, m)))
map_short = partial(map, lambda m: m[0])


def filterMetrics(inputs, node, cluster, invert=False, filter_long=False):
    if isinstance(node, str):
        match = [node]
    else:
        match = node

    for metric_name in inputs:
        dests = list(cluster.getDestinations(metric_name))
        dests = set(map_long(dests)) | set(map_short(dests))

        if dests & set(match):
            if not invert:
                yield metric_name
        else:
            if invert:
                yield metric_name
