import errno
import fileinput
import logging
import sys

from time import time

from .list import listMetrics
from .sieve import filterMetrics
from .util import local_addresses, common_parser
from .lookup import lookup
from .sync import run_batch

from .config import Config
from .cluster import Cluster


def carbon_hosts():
    parser = common_parser('Return the addresses for all nodes in a cluster')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    cluster_hosts = [d[0] for d in cluster.destinations]

    print "\n".join(cluster_hosts)


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


def carbon_sync():
    parser = common_parser(
        'Sync local metrics using remote nodes in the cluster'
        )

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names to filter, or \'-\' ' +
             'to read from STDIN')

    parser.add_argument(
        '-s', '--source-node',
        required=True,
        help='Override the source for metrics data')

    parser.add_argument(
        '-d', '--storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Storage dir')

    parser.add_argument(
        '-b', '--batch-size',
        default=1000,
        help='Batch size for the rsync job')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.metrics_file and args.metrics_file[0] != '-':
        fi = args.metrics_file
    else:
        fi = []

    config = Config(args.config_file)

    user = config.ssh_user()
    remote_ip = args.source_node
    remote = "%s@%s:%s/" % (user, remote_ip, args.storage_dir)

    metrics_to_sync = []

    start = time()
    total_metrics = 0
    batch_size = int(args.batch_size)

    for metric in fileinput.input(fi):
        total_metrics += 1
        metric = metric.strip()
        mpath = metric.replace('.', '/') + "." + "wsp"

        metrics_to_sync.append(mpath)

        if total_metrics % batch_size == 0:
            print "* Running batch %s-%s" \
                  % (total_metrics-batch_size+1, total_metrics)
            run_batch(metrics_to_sync, remote, args.storage_dir)
            metrics_to_sync = []

    if len(metrics_to_sync) > 0:
        print "* Running batch %s-%s" \
              % (total_metrics-len(metrics_to_sync)+1, total_metrics)
        run_batch(metrics_to_sync, remote, args.storage_dir)

    elapsed = (time() - start)

    print ""
    print "* Sync Report"
    print "  ========================================"
    print "  Total metrics synced: %s" % total_metrics
    print "  Total time: %ss" % elapsed
