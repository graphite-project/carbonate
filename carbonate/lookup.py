def lookup(metric, cluster):
    hosts = []
    metric_destinations = cluster.getDestinations(metric)
    for d in metric_destinations:
        hosts.append(':'.join(map(str, d)))
    return hosts
