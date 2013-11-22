from .config import Config
from .cluster import Cluster
from .util import common_parser


def main():
    parser = common_parser('Return the addresses for all nodes in a cluster')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    cluster_hosts = [d[0] for d in cluster.destinations]

    print "\n".join(cluster_hosts)
