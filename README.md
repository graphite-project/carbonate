# Carbonate

> "Pop bottles." *-- Birdman*

[![Build Status](https://travis-ci.org/graphite-project/carbonate.svg?branch=master)](https://travis-ci.org/graphite-project/carbonate)

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
```

You should take care to match the list of destination IPs or hostnames to the nodes in your cluster. Though its worth noting that the ports and labels are currently not used by carbonate. Order is important because of how the consistent hash ring is created.

The replication factor should match the replication factor for the cluster.

Finally, you can choose to provide a SSH user that will be used when carbonate requires connecting to another node in the cluster to perform an operation. If this is not provided, then the current user executing the command will be chosen.

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
                   [--rsync-options [RSYNC_OPTIONS [RSYNC_OPTIONS ...]]]

Sync local metrics using remote nodes in the cluster

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to use (default:
                        /opt/graphite/conf/carbonate.conf)
  -C CLUSTER, --cluster CLUSTER
                        Cluster name (default: main)
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
  --rsync-options [RSYNC_OPTIONS [RSYNC_OPTIONS ...]]
                        Pass option(s) to rsync (default: -azpS)
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
usage: whisper-fill [-h] SRC DST

Backfill datapoints from one whisper file into another

positional arguments:
  SRC         Whisper source file
  DST         Whisper destination file

optional arguments:
  -h, --help  show this help message and exit
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


# License and warnings

These tools should be considered beta quality right now. Tests exist for most functionality, but there is still significant work to be done to make them bullet-proof. However, instead of sitting on this code, I'd rather release it and allow others to provide input and help guide the development. So, expect a few bugs and please help me fix them!

The code is available under the MIT license.
