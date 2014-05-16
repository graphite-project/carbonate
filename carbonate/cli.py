import argparse
import errno
import fileinput
import logging
import os
import sys

from time import time

from .aggregation import setAggregation, AGGREGATION
from .fill import fill_archives
from .list import listMetrics
from .lookup import lookup
from .sieve import filterMetrics
from .sync import run_batch
from .util import local_addresses, common_parser

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
        for m in listMetrics(args.storage_dir):
            print m
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

    parser.add_argument(
        '-s', '--short',
        action='store_true',
        help='Only display the address, without port and cluster name')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    results = lookup(str(args.metric[0]), cluster)

    if args.short:
        for i, _ in enumerate(results):
            results[i] = results[i].split(':')[0]

    print "\n".join(results)


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
        help='Filter for metrics belonging to this node. Uses local addresses ' +
        'if not provided.')

    parser.add_argument(
        '-I', '--invert',
        action='store_true',
        help='Invert the sieve, match metrics that do NOT belong to a node')

    parser.add_argument(
        '--field',
        type=int,
        help='Input field to sieve if multiple metrics per-line of input. ' +
        'Note that fields are indexed starting with 1.')

    parser.add_argument(
        '--field-separator',
        default=',',
        help='Character used to separate metric names when using "--field"')

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
            if args.field is None:
                m = metric.strip()
            else:
                fields = metric.split(args.field_separator)
                try:
                    m = fields[int(args.field)-1].strip()
                except IndexError:
                    raise SystemExit("Field index is out-of-bounds")

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

    parser.add_argument(
        '--source-storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Source storage dir')

    parser.add_argument(
        '--rsync-options',
        default='-azpS',
        help='Pass option(s) to rsync. Make sure to use ' +
        '"--rsync-options=" if option starts with \'-\'')

    parser.add_argument(
        '--rename',
        action='store_true',
        help='Accept a separator delimited pair of metric ' +
        'names as input (e.g. old.metric,new.metric)). Old ' +
        'metrics are *not* removed. See "--rename-separator=\',\'" ' +
        'to control the separator char.')

    parser.add_argument(
        '--rename-separator',
        default=',',
        help='Character used to separate old and new metric ' +
        'names when using "--rename"')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.metrics_file and args.metrics_file[0] != '-':
        fi = args.metrics_file
    else:
        fi = []

    config = Config(args.config_file)

    user = config.ssh_user()
    remote_ip = args.source_node
    remote = "%s@%s:%s/" % (user, remote_ip, args.source_storage_dir)

    metrics_to_sync = []

    start = time()
    total_metrics = 0
    batch_size = int(args.batch_size)

    for metric in fileinput.input(fi):
        total_metrics += 1
        if args.rename:
            (old_metric, new_metric) = metric.split(args.rename_separator)
        else:
            (old_metric, new_metric) = (metric, metric)

        old_metric = old_metric.strip()
        new_metric = new_metric.strip()
        old_mpath = old_metric.replace('.', '/') + "." + "wsp"
        new_mpath = new_metric.replace('.', '/') + "." + "wsp"

        metrics_to_sync.append((old_mpath, new_mpath))

        if total_metrics % batch_size == 0:
            print "* Running batch %s-%s" \
                  % (total_metrics-batch_size+1, total_metrics)
            run_batch(metrics_to_sync, remote,
                      args.storage_dir, args.rsync_options)
            metrics_to_sync = []

    if len(metrics_to_sync) > 0:
        print "* Running batch %s-%s" \
              % (total_metrics-len(metrics_to_sync)+1, total_metrics)
        run_batch(metrics_to_sync, remote,
                  args.storage_dir, args.rsync_options)

    elapsed = (time() - start)

    print ""
    print "* Sync Report"
    print "  ========================================"
    print "  Total metrics synced: %s" % total_metrics
    print "  Total time: %ss" % elapsed


def whisper_aggregate():
    parser = argparse.ArgumentParser(
        description='Set aggregation for whisper-backed metrics this carbon ' +
                    'instance contains',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names and aggregation modes, or \'-\' ' +
             'to read from STDIN')

    parser.add_argument(
        '-d', '--storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Whisper storage directory')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.metrics_file and args.metrics_file[0] != '-':
        fi = args.metrics_file
        metrics = map(lambda s: s.strip(), fileinput.input(fi))
    else:
        metrics = map(lambda s: s.strip(), fileinput.input([]))

    metrics_count = 0

    for metric in metrics:
        name, t = metric.strip().split('|')

        mode = AGGREGATION[t]
        if mode is not None:
            cname = name.replace('.', '/')
            path = os.path.join(args.storage_dir, cname + '.wsp')
            metrics_count = metrics_count + setAggregation(path, mode)

    logging.info('Successfully set aggregation mode for ' +
                 '%d of %d metrics' % (metrics_count, len(metrics)))


def whisper_fill():
    parser = argparse.ArgumentParser(
        description='Backfill datapoints from one whisper file into another',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'source',
        metavar='SRC',
        help='Whisper source file')

    parser.add_argument(
        'dest',
        metavar='DST',
        help='Whisper destination file')

    args = parser.parse_args()

    src = args.source
    dst = args.dest

    if not os.path.isfile(src):
        raise SystemExit('Source file not found.')

    if not os.path.isfile(dst):
        raise SystemExit('Destination file not found.')

    startFrom = time()

    fill_archives(src, dst, startFrom)
