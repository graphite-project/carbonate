import argparse
import errno
import logging
import os
import sys

from functools import partial
from time import time

from .aggregation import setAggregation, AGGREGATION
from .fill import fill_archives
from .list import listMetrics
from .lookup import lookup
from .sieve import filterMetrics
from .stale import data, stat
from .sync import run_batch
from .util import (
    local_addresses, common_parser, metric_to_fs, fs_to_metric,
    metrics_from_args,
)

from .config import Config
from .cluster import Cluster


STORAGE_DIR = '/opt/graphite/storage/whisper'


def carbon_hosts():
    parser = common_parser('Return the addresses for all nodes in a cluster')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster)

    cluster_hosts = [d[0] for d in cluster.destinations]

    print("\n".join(cluster_hosts))


def carbon_list():
    parser = common_parser('List the metrics this carbon node contains')

    parser.add_argument(
        '-d', '--storage-dir',
        default=STORAGE_DIR,
        help='Storage dir')

    parser.add_argument(
        '-s', '--follow-sym-links',
        action='store_true',
        help='Follow sym links')

    args = parser.parse_args()

    try:
        for m in listMetrics(args.storage_dir, args.follow_sym_links):
            print(m)
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
        '-a', '--aggregation-rules',
        default='/opt/graphite/conf/aggregation-rules.conf',
        help='File containing rules used in conjunction with the ' +
             '"aggregated-consistent-hashing" relay method')

    parser.add_argument(
        '-s', '--short',
        action='store_true',
        help='Only display the address, without port and cluster name')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster, args.aggregation_rules)

    results = lookup(str(args.metric[0]), cluster)

    if args.short:
        for i, _ in enumerate(results):
            results[i] = results[i].split(':')[0]

    print("\n".join(results))


def carbon_sieve():
    parser = common_parser(
        'Given a list of metrics, output those that belong to a node')

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names to filter, or \'-\' ' +
             'to read from STDIN')

    parser.add_argument(
        '-a', '--aggregation-rules',
        default='/opt/graphite/conf/aggregation-rules.conf',
        help='File containing rules used in conjunction with the ' +
             '"aggregated-consistent-hashing" relay method')

    parser.add_argument(
        '-n', '--node',
        help='Filter for metrics belonging to this node. Uses the local ' +
             'addresses if not provided.')

    parser.add_argument(
        '-I', '--invert',
        action='store_true',
        help='Invert the sieve, match metrics that do NOT belong to a node')

    args = parser.parse_args()

    config = Config(args.config_file)
    cluster = Cluster(config, args.cluster, args.aggregation_rules)
    invert = args.invert

    metrics = metrics_from_args(args)

    if args.node:
        match_dests = [args.node]
    else:
        match_dests = local_addresses()

    try:
        for metric in metrics:
            m = metric.strip()
            for match in filterMetrics([m], match_dests, cluster, invert):
                print(metric.strip())
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
        default=STORAGE_DIR,
        help='Storage dir')

    parser.add_argument(
        '-b', '--batch-size',
        default=1000,
        help='Batch size for the rsync job')

    parser.add_argument(
        '--source-storage-dir',
        default=STORAGE_DIR,
        help='Source storage dir')

    parser.add_argument(
        '--rsync-options',
        default='-azpS',
        help='Pass option(s) to rsync. Make sure to use ' +
        '"--rsync-options=" if option starts with \'-\'')

    parser.add_argument(
        '--rsync-disable-copy-dest',
        default=False,
        action='store_true',
        help='Avoid --copy-dest, transfer all whisper data between nodes.')

    parser.add_argument(
        '--dirty',
        action='store_true',
        help="If set, don't clean temporary rsync directory")

    parser.add_argument(
        '-l', '--lock',
        default=False,
        action='store_true',
        help='Lock whisper files during filling')

    parser.add_argument(
        '-o', '--overwrite',
        default=False,
        dest='overwrite',
        action='store_true',
        help='Write all non nullpoints from src to dst')

    parser.add_argument(
        '-t', '--tmpdir',
        default=None,
        help='Specify where temporary rsync directories will be created')

    parser.add_argument(
        '--rsync-max-retries',
        type=int,
        default=3,
        help='Maximum number of rsync attempts for each batch of metrics')

    parser.add_argument(
        '--rsync-retries-interval',
        default=5,
        help='How long to wait (in seconds) between rsync retry attempts')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config = Config(args.config_file)

    user = config.ssh_user(args.cluster)
    remote_ip = args.source_node
    remote = "%s@%s:%s/" % (user, remote_ip, args.source_storage_dir)

    whisper_lock_writes = config.whisper_lock_writes(args.cluster) or \
        args.lock

    metrics_to_sync = []
    metrics = metrics_from_args(args)

    start = time()
    total_metrics = 0
    batch_size = int(args.batch_size)

    rsync_options = args.rsync_options
    if not args.rsync_disable_copy_dest:
        rsync_options += ' --copy-dest="%s"' % args.storage_dir

    for metric in metrics:
        total_metrics += 1
        metric = metric.strip()
        mpath = metric_to_fs(metric)

        metrics_to_sync.append(mpath)

        if total_metrics % batch_size == 0:
            print("* Running batch %s-%s"
                  % (total_metrics-batch_size+1, total_metrics))
            run_batch(metrics_to_sync, remote,
                      args.storage_dir, rsync_options,
                      remote_ip, args.dirty, lock_writes=whisper_lock_writes,
                      overwrite=args.overwrite, tmpdir=args.tmpdir,
                      rsync_max_retries=args.rsync_max_retries,
                      rsync_retries_interval=args.rsync_retries_interval)
            metrics_to_sync = []

    if len(metrics_to_sync) > 0:
        print("* Running batch %s-%s"
              % (total_metrics-len(metrics_to_sync)+1, total_metrics))
        run_batch(metrics_to_sync, remote,
                  args.storage_dir, rsync_options,
                  remote_ip, args.dirty, lock_writes=whisper_lock_writes,
                  overwrite=args.overwrite, tmpdir=args.tmpdir,
                  rsync_max_retries=args.rsync_max_retries,
                  rsync_retries_interval=args.rsync_retries_interval)

    elapsed = (time() - start)

    print("")
    print("* Sync Report")
    print("  ========================================")
    print("  Total metrics synced: %s" % total_metrics)
    print("  Total time: %ss" % elapsed)


def carbon_path():
    # Use common_parser for consistency, even though we do not use any config
    # file options at present.
    parser = common_parser(
        'Transform metric paths to (or from) filesystem paths'
    )

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names to transform to file paths, or ' +
        '\'-\' to read from STDIN')

    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help='Transform from file paths to metric paths'
    )

    parser.add_argument(
        '-p', '--prepend',
        action='store_true',
        help='Prepend storage dir to file paths')

    parser.add_argument(
        '-d', '--storage-dir',
        default=STORAGE_DIR,
        help='Whisper storage directory to prepend or strip')

    args = parser.parse_args()
    metrics = metrics_from_args(args)
    if args.reverse:
        # Always try to strip storage dir when doing fs->metric.
        # Nobody would ever not want that.
        func = partial(fs_to_metric, prepend=args.storage_dir)
    else:
        # Only give non-empty prepend if -p given, when metric->fs
        prepend = args.storage_dir if args.prepend else None
        func = partial(metric_to_fs, prepend=prepend)

    for metric in metrics:
        print(func(metric))


def carbon_stale():
    # Use common_parser for consistency, even though we do not use any config
    # file options at present.
    parser = common_parser(
        'Find and list potentially stale metrics.'
    )

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names to scan for staleness, or ' +
        '\'-\' to read from STDIN')

    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help='Output metrics which are not stale instead')

    parser.add_argument(
        '-d', '--storage-dir',
        default=STORAGE_DIR,
        help='Whisper storage directory to prepend when -p given')

    parser.add_argument(
        '-l', '--limit', metavar='HOURS',
        type=int, default=24,
        help='Definition of staleness, in hours')

    parser.add_argument(
        '-o', '--offset', metavar='HOURS',
        type=int, default=0,
        help='Use a whisper data window ending HOURS ago (implies -w)')

    parser.add_argument(
        '-w', '--whisper',
        action='store_true',
        help='Use whisper data instead of filesystem stat() call')

    parser.add_argument(
        '-p', '--paths',
        action='store_true',
        help='Print filesystem paths instead of metric names')

    args = parser.parse_args()
    metrics = metrics_from_args(args)
    prefix = args.storage_dir
    use_whisper = args.whisper or args.offset
    for path in map(partial(metric_to_fs, prepend=prefix), metrics):
        passed = (data if use_whisper else stat)(path, args.limit, args.offset)
        value = path if args.paths else fs_to_metric(path, prepend=prefix)
        if (not passed) if args.reverse else passed:
            print(value)


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
        default=STORAGE_DIR,
        help='Whisper storage directory')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    metrics = metrics_from_args(args)

    metrics_count = 0

    for metric in metrics:
        try:
            name, t = metric.strip().split('|')

            mode = AGGREGATION[t]
            if mode is not None:
                path = metric_to_fs(name, prepend=args.storage_dir)
                metrics_count = metrics_count + setAggregation(path, mode)
        except ValueError as exc:
            logging.warning("Unable to parse '%s' (%s)" % (metric, str(exc)))

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

    parser.add_argument(
        '-l', '--lock',
        default=False,
        action='store_true',
        help='Lock whisper files during filling')

    parser.add_argument(
        '-o', '--overwrite',
        default=False,
        dest='overwrite',
        action='store_true',
        help='Write all non nullpoints from src to dst')

    args = parser.parse_args()

    src = args.source
    dst = args.dest

    if not os.path.isfile(src):
        raise SystemExit('Source file not found.')

    if not os.path.isfile(dst):
        raise SystemExit('Destination file not found.')

    startFrom = time()

    fill_archives(src, dst, startFrom, lock_writes=args.lock,
                  overwrite=args.overwrite)
