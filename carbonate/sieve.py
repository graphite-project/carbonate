import fileinput
import sys

from .config import Config
from .cluster import Cluster
from .util import local_addresses, common_parser


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


def main():
    parser = common_parser(
        'Given a list of metrics, output those that belong to a node')

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names to filter, or \'-\' ' +
             'to read from STDIN')

    parser.add_argument(
        '-n', '--node',
        default="self",
        help='Filter for metrics belonging to this node')

    parser.add_argument(
        '-I', '--invert',
        action='store_true',
        help='Invert the sieve, match metrics that do NOT belong to a node')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)
    invert = args.invert

    if args.metrics_file and args.metrics_file[0] != '-':
        fi = args.metrics_file
    else:
        fi = []

    if args.node:
        match_dests = [args.node]
    else:
        match_dests = local_addresses()

    try:
        for metric in fileinput.input(fi):
            m = metric.strip()
            for match in filterMetrics([m], match_dests, cluster, invert):
                print metric.strip()
    except KeyboardInterrupt:
        sys.exit(1)
