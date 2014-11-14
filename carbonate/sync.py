import os
import sys
import logging
import shutil
import subprocess
from time import time
from datetime import timedelta
from tempfile import mkdtemp, NamedTemporaryFile
from shutil import rmtree
from whisper import CorruptWhisperFile

from .fill import fill_archives


def sync_from_remote(sync_file, remote, staging, rsync_options):
    try:
        try:
            os.makedirs(os.path.dirname(staging))
        except OSError:
            pass

        cmd = " ".join(['rsync', rsync_options, '--files-from',
                        sync_file.name, remote, staging
                        ])

        print "  - Rsyncing metrics"

        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        for l in iter(proc.stdout.readline, b''):
            sys.stdout.write(l)
            sys.stdout.flush()
    except subprocess.CalledProcessError as e:
        logging.warn("Failed to sync from %s! %s" % (remote, e))


def sync_batch(metrics_to_heal):
    batch_start = time()
    sync_count = 0
    sync_total = len(metrics_to_heal)
    sync_avg = 0.1
    sync_remain = 'n/a'

    for (staging, local) in metrics_to_heal:
        sync_count += 1
        sync_start = time()
        sync_percent = float(sync_count) / sync_total * 100
        status_line = "  - Syncing %d of %d metrics. " \
                      "Avg: %fs  Time Left: %ss (%d%%)" \
                      % (sync_count, sync_total, sync_avg,
                         sync_remain, sync_percent)
        print status_line

        heal_metric(staging, local)

        sync_elapsed = time() - sync_start
        sync_avg = sync_elapsed / sync_count
        sync_remain_s = sync_avg * (sync_total - sync_count)
        sync_remain = str(timedelta(seconds=sync_remain_s))

    batch_elapsed = time() - batch_start
    return batch_elapsed


def sync_batch_parallel(metrics_to_heal):
    "sync a batch of metrics, using gnu parallel to parallelize the merges"
    batch_start = time()

    print "  - Merging metrics - setup"
    # setup a gnu parallel input
    parallel_stdin = []
    for (staging, local) in metrics_to_heal:
        if not os.path.exists(local):
            parallel_stdin.append("mkdir -p %s" % os.path.dirname(local))
            parallel_stdin.append("cp %s %s" % (staging, local))
        else:
            parallel_stdin.append("whisper-fill %s %s" % (staging, local))
    # invoke gnu parallel with this input
    print "  - Merging metrics - parallel"
    p = subprocess.Popen("parallel",
                         shell=True,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate(input="\n".join(parallel_stdin))
    print stdout
    print stderr

    batch_elapsed = time() - batch_start
    return batch_elapsed


def heal_metric(source, dest):
    try:
        with open(dest):
            try:
                fill_archives(source, dest, time())
            except CorruptWhisperFile as e:
                logging.warn("Overwriting corrupt file %s!" % dest)
                try:
                    os.makedirs(os.path.dirname(dest))
                except os.error:
                    pass
                try:
                    shutil.copyfile(source, dest)
                except IOError as e:
                    logging.warn("Failed to copy %s! %s" % (dest, e))
    except IOError:
        try:
            os.makedirs(os.path.dirname(dest))
        except os.error:
            pass
        try:
            shutil.copyfile(source, dest)
        except IOError as e:
            logging.warn("Failed to copy %s! %s" % (dest, e))


def run_batch(metrics_to_sync, remote, local_storage, rsync_options, parallel):
    staging_dir = mkdtemp()
    sync_file = NamedTemporaryFile(delete=False)

    metrics_to_heal = []

    staging = "%s/" % (staging_dir)

    for metric in metrics_to_sync:
        staging_file = "%s/%s" % (staging_dir, metric)
        local_file = "%s/%s" % (local_storage, metric)
        metrics_to_heal.append((staging_file, local_file))

    sync_file.write("\n".join(metrics_to_sync))
    sync_file.flush()

    rsync_start = time()

    sync_from_remote(sync_file, remote, staging, rsync_options)

    rsync_elapsed = (time() - rsync_start)

    if parallel:
        merge_elapsed = sync_batch_parallel(metrics_to_heal)
    else:
        merge_elapsed = sync_batch(metrics_to_heal)

    total_time = rsync_elapsed + merge_elapsed

    print "    --------------------------------------"
    print "    Rsync time: %ss" % rsync_elapsed
    print "    Merge time: %ss" % merge_elapsed
    print "    Total time: %ss" % total_time

    # Cleanup
    rmtree(staging_dir)
    os.unlink(sync_file.name)
