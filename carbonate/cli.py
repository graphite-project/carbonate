import errno
import fileinput
import sys

from .list import listMetrics
from .sieve import filterMetrics
from .util import local_addresses, common_parser
from .lookup import lookup

from .config import Config
from .cluster import Cluster


def carbon_list():
    parser = common_parser('List the metrics this carbon node contains')

    parser.add_argument(
        '-d', '--storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Storage dir')

    args = parser.parse_args()

    try:
        listMetrics(args.storage_dir)
    except IOError as e:
        if e.errno == errno.EPIPE:
            pass  # we got killed, lol
        else:
            raise SystemExit(e)
    except KeyboardInterrupt:
        sys.exit(1)


def carbon_lookup():
    parser = common_parser('Lookup where a metric lives in a carbon cluster')

    parser.add_argument(
        'metric', metavar='METRIC', nargs=1,
        type=str,
        help='Full metric name to search for')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    print "\n".join(lookup(str(args.metric[0]), cluster))


def carbon_sieve():
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
