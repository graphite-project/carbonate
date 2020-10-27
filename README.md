# Carbonate

> "Pop bottles." *-- Birdman*

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/99e1654102b74d82a63505145334e7ed)](https://www.codacy.com/app/graphite-project/carbonate?utm_source=github.com&utm_medium=referral&utm_content=graphite-project/carbonate&utm_campaign=badger)
[![Build Status](https://travis-ci.org/graphite-project/carbonate.svg?branch=master)](https://travis-ci.org/graphite-project/carbonate)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fgraphite-project%2Fcarbonate.svg?type=shield)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fgraphite-project%2Fcarbonate?ref=badge_shield)
[![codecov](https://codecov.io/gh/graphite-project/carbonate/branch/master/graph/badge.svg)](https://codecov.io/gh/graphite-project/carbonate)

Graphite clusters are pretty cool. Here are some primitive tools to help you manage your graphite clusters.

All of the tools support two common arguments; the path to a config file, and the name of the cluster. Using these tools alongside a config file that describes your graphite clusters you can build up scripts to manage your metrics. Some of the tools could easily be replaced with one-liners in shell, but exist here for convenience and readability. The goal is to provide fast, predictable utilities that can easily be composed into more advanced tooling.

## Install
[Carbonate is available from Python official third party repository](https://pypi.python.org/pypi/carbonate/0.2.1) (aka PyPi) and as such can be installed via regular Python package managers.
Note that you might have to install a python package manager (e.g. apt-get install python-setuptools on a ubuntu host)

```
pip install carbonate
```
## The Config

Carbonate expects a configuration file that defines the clusters in your environment. The default config file is located at `/opt/graphite/conf/carbonate.conf` or can be provided on the command line. The default cluster is named 'main'. Both defaults can be overridden by setting in the environment `CARBONATE_CONFIG` and `CARBONATE_CLUSTER` respectively.

```
[main]
DESTINATIONS = 192.168.9.13:2004:carbon01, 192.168.9.15:2004:carbon02, 192.168.6.20:2004:carbon03
REPLICATION_FACTOR = 2
SSH_USER = carbon

[agg]
DESTINATIONS = 192.168.9.13:2004:carbon01, 192.168.9.15:2004:carbon02, 192.168.6.20:2004:carbon03
RELAY_METHOD = aggregated-consistent-hashing
REPLICATION_FACTOR = 2
SSH_USER = carbon

[fnv]
DESTINATIONS = 192.168.9.13:2004:ba603c36342304ed77953f84ac4d357b, 192.168.9.15:2004:5dd63865534f84899c6e5594dba6749a, 192.168.6.20:2004:866a18b81f2dc4649517a1df13e26f28
REPLICATION_FACTOR = 2
SSH_USER = carbonate
HASHING_TYPE = fnv1a_ch
```

You should take care to match the list of destination IPs or hostnames to the nodes in your cluster (i.e. it should match with routing configuretion of your carbon relay). Order is important because of how the consistent hash ring is created.

You can configure the relay method to be one of "consistent-hashing" or "aggregated-consistent-hashing". If omitted, "consistent-hashing" is used by default. Use of "aggregated-consistent-hashing" usually requires a rules file to be provided to relevant commands.

The replication factor should match the replication factor for the cluster.

Also, you can choose to provide a SSH user that will be used when carbonate requires connecting to another node in the cluster to perform an operation. If this is not provided, then the current user executing the command will be chosen.

Finally, you can provide HASHING_TYPE of your cluster. Default is `carbon_ch`, also `fnv1a_ch` is supported. Please note that for using `fnv1a_ch` hashing you need `carbon` 1.0.2 or newer installed (or you need to use [carbon-c-relay](https://github.com/grobian/carbon-c-relay) relay instead).

## The Tools

### carbon-hosts

```
usage: carbon-hosts [-h] [-c CONFIG_FILE] [-C CLUSTER]

Return the addresses for all nodes in a cluster

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
```

### carbon-lookup

```
usage: carbon-lookup [-h] [-c CONFIG_FILE] [-C CLUSTER] [-s] METRIC

Lookup where a metric lives in a carbon cluster

positional arguments:
  METRIC                Full metric name to search for

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
  -a AGGREGATION_RULES, --aggregation-rules AGGREGATION_RULES
                        File containing rules used in conjunction with the
                        "aggregated-consistent-hashing" relay method (default:
                        /opt/graphite/conf/aggregation-rules.conf)
  -s, --short           Only display the address, without port and cluster
                        name (default: False)
```

### carbon-list

```
usage: carbon-list [-h] [-c CONFIG_FILE] [-C CLUSTER] [-d STORAGE_DIR]

List the metrics this carbon node contains

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
  -d STORAGE_DIR, --storage-dir STORAGE_DIR
                        Storage dir (default: /opt/graphite/storage/whisper)
```

### carbon-sieve

```
usage: carbon-sieve [-h] [-c CONFIG_FILE] [-C CLUSTER] [-f METRICS_FILE]
                    [-n NODE] [-I]

Given a list of metrics, output those that belong to a node

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
  -a AGGREGATION_RULES, --aggregation-rules AGGREGATION_RULES
                        File containing rules used in conjunction with the
                        "aggregated-consistent-hashing" relay method (default:
                        /opt/graphite/conf/aggregation-rules.conf)
  -f METRICS_FILE, --metrics-file METRICS_FILE
                        File containing metric names to filter, or '-' to read
                        from STDIN (default: -)
  -n NODE, --node NODE  Filter for metrics belonging to this node (default:
                        self)
  -I, --invert          Invert the sieve, match metrics that do NOT belong to
                        a node (default: False)
```

### carbon-sync

```
usage: carbon-sync [-h] [-c CONFIG_FILE] [-C CLUSTER] [-f METRICS_FILE] -s
                   SOURCE_NODE [-d STORAGE_DIR] [-b BATCH_SIZE]
                   [--source-storage-dir SOURCE_STORAGE_DIR]
                   [--rsync-options RSYNC_OPTIONS] [--rsync-disable-copy-dest]
                   [--tmpdir TMP_STAGING_DIR] [--rsync-max-retries MAX_RETRIES]
                   [--rsync-retries-interval SECONDS] [--dirty] [-l] [-o]

Sync local metrics using remote nodes in the cluster

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (env: CARBONATE_CONFIG) (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (env: CARBONATE_CLUSTER) (default: main)
  -f METRICS_FILE, --metrics-file METRICS_FILE
                        File containing metric names to filter, or '-' to read
                        from STDIN (default: -)
  -s SOURCE_NODE, --source-node SOURCE_NODE
                        Override the source for metrics data (default: None)
  -d STORAGE_DIR, --storage-dir STORAGE_DIR
                        Storage dir (default: /opt/graphite/storage/whisper)
  -b BATCH_SIZE, --batch-size BATCH_SIZE
                        Batch size for the rsync job (default: 1000)
  --source-storage-dir SOURCE_STORAGE_DIR
                        Source storage dir (default:
                        /opt/graphite/storage/whisper)
  --rsync-options RSYNC_OPTIONS
                        Pass option(s) to rsync. Make sure to use "--rsync-
                        options=" if option starts with '-' (default: -azpS)
  --rsync-disable-copy-dest
                        Avoid --copy-dest, transfer all whisper data between
                        nodes. (default: False)
  --rsync-max-retries RETRIES
                        Number of times rsync will attempt to copy each batch
                        of metrics before moving on. If all retry attempts are
                        unsuccessful, carbon-sync will write a file containing
                        the name of each metric in the failed batch so they can
                        be easily retried at a later time. (Default: 3)
  --rsync-retries-interval SECONDS
                        How long to wait in between each rsync retry attempt
                        (see --rsync-max-retries). (default: 5)
  -t TMP_STAGING_DIR, --tmpdir TMP_STAGING_DIR
                        Specify an alternate location in which the temporary
                        rsync staging dirs will be created. This can be useful
                        for large syncs where the default location (as chosen
                        by mkdtemp) resides on a filesystem that's too small
                        to store all the metrics being copied from the remote
                        host.
  --dirty               If set, don't clean temporary rsync directory
                        (default: False)
  -l, --lock            Lock whisper files during filling (default: False)
  -o, --overwrite       Write all non nullpoints from src to dst (default:
                        False)
```

### carbon-path

```
usage: carbon-path [-h] [-c CONFIG_FILE] [-C CLUSTER] [-f METRICS_FILE] [-r]
                   [-p] [-d STORAGE_DIR]

Transform metric paths to (or from) filesystem paths

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
  -f METRICS_FILE, --metrics-file METRICS_FILE
                        File containing metric names to transform to file
                        paths, or '-' to read from STDIN (default: -)
  -r, --reverse         Transform from file paths to metric paths (default:
                        False)
  -p, --prepend         Prepend storage dir to file paths (default: False)
  -d STORAGE_DIR, --storage-dir STORAGE_DIR
                        Whisper storage directory to prepend when -p given
                        (default: /opt/graphite/storage/whisper)
```

### carbon-stale

```
usage: carbon-stale [-h] [-c CONFIG_FILE] [-C CLUSTER] [-f METRICS_FILE] [-r]
                    [-d STORAGE_DIR] [-l HOURS] [-o HOURS] [-w] [-p]

Find and list potentially stale metrics.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
  -f METRICS_FILE, --metrics-file METRICS_FILE
                        File containing metric names to transform to file
                        paths, or '-' to read from STDIN (default: -)
  -r, --reverse         Output metrics which are not stale instead (default:
                        False)
  -d STORAGE_DIR, --storage-dir STORAGE_DIR
                        Whisper storage directory to prepend when -p given
                        (default: /opt/graphite/storage/whisper)
  -l HOURS, --limit HOURS
                        Definition of staleness, in hours (default: 24)
  -o HOURS, --offset HOURS
                        Use a whisper data window ending HOURS ago (implies
                        -w) (default: 0)
  -w, --whisper         Use whisper data instead of filesystem stat() call
                        (default: False)
  -p, --paths           Print filesystem paths instead of metric names
                        (default: False)
```

### whisper-aggregate

```
usage: whisper-aggregate [-h] [-f METRICS_FILE] [-d STORAGE_DIR]

Set aggregation for whisper-backed metrics this carbon instance contains

optional arguments:
  -h, --help            show this help message and exit
  -f METRICS_FILE, --metrics-file METRICS_FILE
                        File containing metric names and aggregation modes, or
                        '-' to read from STDIN (default: -)
  -d STORAGE_DIR, --storage-dir STORAGE_DIR
                        Whisper storage directory (default:
                        /opt/graphite/storage/whisper)
```

### whisper-fill

```
usage: whisper-fill [-h] [-l] [-o] SRC DST

Backfill datapoints from one whisper file into another

positional arguments:
  SRC             Whisper source file
  DST             Whisper destination file

optional arguments:
  -h, --help      show this help message and exit
  -l, --lock      Lock whisper files during filling (default: False)
  -o, --overwrite  Write all non nullpoints from src to dst (default: False)
```

## Example usage

### Resync a node in a cluster

```
#!/bin/sh
#
# Resync a node from other nodes in the cluster
#

LOCAL_IP="$1"

for h in $(carbon-hosts) ; do
  (
    ssh $h -- carbon-list |
    carbon-sieve -n $LOCAL_IP |
    carbon-sync -s $h
  ) &
done
```

### Rebalance a cluster

```
#!/bin/sh
#
# Rebalance a cluster from one size to another. Remember to cleanup metrics
# that no longer belong when all nodes are rebalanced!
#

LOCAL_IP="$1"
OLD_CLUSTER="old"
NEW_CLUSTER="main"

for h in $(carbon-hosts -C "$OLD_CLUSTER") ; do
  ssh $h -- carbon-list |
  carbon-sieve -C "$NEW_CLUSTER" -n $LOCAL_IP |
  carbon-sync -s $h
done
```

### List metrics that don't belong

```
#!/bin/sh
#
# List metrics from disk that don't belong
#

LOCAL_IP="$1"

carbon-list | carbon-sieve -I -n $LOCAL_IP
```

### Listing metrics that have stopped updating

Metrics with whisper data that is entirely blank for the last 2 hours (perhaps
useful if you suspect issues with fs timestamps or carbon clients writing in 'the
future'):

```
carbon-list | carbon-stale --whisper --limit=2
```

Metrics whose metrics files appear untouched for 48 hours or more (functionally
identical to `find /your/data/dir -type f -mtime +2`):

```
carbon-list | carbon-stale --limit=48
```

More interesting is if you use ``carbon-stale``, then sieve to identify stale
metrics that don't belong here (vs un-stale metrics that *do* belong here but
are misreported in carbon-sieve due to things like doubled-up periods in metric
paths due to broken collectors. It's a thing.)

```
carbon-list | carbon-stale --limit=48 | carbon-sieve -I -n $LOCAL_IP
```

To print file paths for use with e.g. `xargs rm` or whatnot, use `-p`:

```
carbon-list | carbon-stale -p | xargs -n 100 rm
```


# License

The code is available under the MIT license.



