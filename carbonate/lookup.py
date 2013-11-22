from .config import Config
from .cluster import Cluster
from .util import common_parser


def lookup(metric, cluster):
    hosts = []
    metric_destinations = cluster.getDestinations(metric)
    for d in metric_destinations:
        hosts.append(':'.join(map(str, d)))
    return hosts


def main():
    parser = common_parser('Lookup where a metric lives in a carbon cluster')

    parser.add_argument(
        'metric', metavar='METRIC', nargs=1,
        type=str,
        help='Full metric name to search for')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    print "\n".join(lookup(str(args.metric[0]), cluster))
